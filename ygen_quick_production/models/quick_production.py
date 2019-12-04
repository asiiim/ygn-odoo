# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import Warning, ValidationError, UserError
from odoo.tools import float_compare, float_round
from odoo.addons import decimal_precision as dp

import logging

_logger = logging.getLogger(__name__)

class QuickProduction(models.Model):
    _name = 'ygen.quick.production'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Quick Production"
    _order = "id desc"

    # Quick Production Reference
    name = fields.Char(string="Reference", required=True, copy=False, readonly=True, index=True, default=lambda self: _('New Quick Production'), track_visibility='onchange')

    company_id = fields.Many2one(
        'res.company', 'Company',
        readonly=True, index=True, required=True,
        default=lambda self: self.env['res.company']._company_default_get('mrp.production'))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'ygen.quick.production') or _('New Quick Production')
        
        # Check if other records are in draft or start state
        quick_productions = self.env['ygen.quick.production'].search([])
        for qp in quick_productions:
            if qp.state in ('draft', 'start'):
                raise UserError(_('You have other production(s) in draft or start state.\nMake sure they are done first.'))
    
        result = super(QuickProduction, self).create(vals)
        return result
    
    # Stock Default Location
    @api.model
    def _default_location_id(self):
        company_user = self.env.user.company_id
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_user.id)], limit=1)
        if warehouse:
            return warehouse.lot_stock_id
        else:
            raise UserError(_('You must define a warehouse for the company: %s.') % (company_user.name))
    

    location_id = fields.Many2one('stock.location', string='Finish Location', required=True, track_visibility='onchange', domain="[('usage', '=', 'internal'), ('company_id', '=', company_id)]", default=_default_location_id)
    raw_location_id = fields.Many2one('stock.location', string='Source Location', required=True, track_visibility='onchange', domain="[('usage', '=', 'internal'), ('company_id', '=', company_id)]", default=_default_location_id)


    date = fields.Datetime(string='Order Date', required=True, copy=False, default=fields.Datetime.now, track_visibility='onchange')
    quick_prod_tmpl_id = fields.Many2one('ygen.quick.production.template', string="Production Template", track_visibility='onchange')
    product_line_ids = fields.One2many('quick.production.line', 'quick_production_id', string="Product Lines", track_visibility='onchange')
    quant_ids = fields.One2many(related="location_id.quant_ids")

    # Get values from the template
    @api.onchange('quick_prod_tmpl_id')
    def on_change_template(self):
        if not self.quick_prod_tmpl_id:
            return
        
        template = self.quick_prod_tmpl_id
        template.refresh_on_hand()
        self.location_id = template.location_id
        self.raw_location_id = template.raw_location_id
        self.get_template_product_lines(template)

    # Start sale
    state = fields.Selection(string='Status', selection=[
        ('draft', 'Draft'),
        ('start', 'Start'),
        ('validate', 'Validate')],
        copy=False, index=True, readonly=True,
        default='draft', track_visibility='onchange')

    # Get Template
    def get_template_product_lines(self, template):
        if template:
            product_lines = [(5, 0, 0)]
            for line in template.product_line_ids:
                if line.sys_on_hand <= 0:
                    data = {
                        'quick_production_id':self.id,
                        'sequence': line.sequence,
                        'product_id': line.product_id,
                        'to_produce': 0.0,
                        'sys_on_hand': line.sys_on_hand,
                        'bom_id': line.bom_id
                    }
                    product_lines.append((0, 0, data))
            self.product_line_ids = product_lines

    def action_start(self):
        for rec in self.filtered(lambda x: x.state == 'draft'):
            vals = {
                'state': 'start', 
                'date': fields.Datetime.now()
            }
            rec.write(vals)
            if not self.product_line_ids:
                rec.quick_prod_tmpl_id.refresh_on_hand()
                rec.get_template_product_lines(rec.quick_prod_tmpl_id)
        return True
    
    def action_cancel(self):
        for rec in self.filtered(lambda x: x.state not in ('draft', 'validate')):
            vals = {
                'state': 'draft', 
                'date': fields.Datetime.now(),
                'product_line_ids': [(5, 0, 0)]
            }
            rec.write(vals)
        return True
    
    # Prepare manufature orders for each product
    mrp_prod_ids = fields.One2many('mrp.production', 'quick_production_id', string='Manufacturing Orders')
    mrp_prod_count = fields.Integer(string='Manufacturing Orders', compute='_computer_manufacturing_order_lens')

    @api.depends('state')
    def _computer_manufacturing_order_lens(self):
        for rec in self:
            rec.update({
                'mrp_prod_count': len(rec.mrp_prod_ids)
            })
    

    # Prepare Manufacture Order
    @api.multi
    def _prepare_mo(self, product, qty, bom_id):
        self.ensure_one()
        mo_vals = {
            'location_src_id': self.raw_location_id.id,
            'location_dest_id': self.location_id.id,
            'date_planned_start': self.date,
            'product_id': product.id,
            'product_uom_id': product.uom_id.id,
            'product_qty': qty,
            'bom_id': bom_id,
            'quick_production_id': self.id
        }
        return mo_vals
    
    def action_validate(self):
        # Create Manufacturing Orders and Confirm it 
        if self.product_line_ids:
            ManufacturingOrder = self.env['mrp.production']
            
            for line in self.product_line_ids:
                vals = self._prepare_mo(line.product_id, line.to_produce, line.bom_id.id)
                production_id = ManufacturingOrder.create(vals)
                self.do_produce(line.product_id, line.to_produce, line.product_id.uom_id, production_id)

        for rec in self.filtered(lambda x: x.state == 'start'):
            vals = {
                'state': 'validate', 
                'date': fields.Datetime.now(),
            }
            rec.write(vals)
    
    # Do Production Process
    @api.multi
    def do_produce(self, product, qty, uom, production):
        quantity = qty
        if float_compare(quantity, 0, precision_rounding=uom.rounding) <= 0:
            raise UserError(_("The production order for '%s' has no quantity specified") % product.display_name)
        for move in production.move_raw_ids:
            if move.product_id.tracking == 'none' and move.state not in ('done', 'cancel') and move.unit_factor:
                rounding = move.product_uom.rounding
                if product.tracking != 'none':
                    qty_to_add = float_round(quantity * move.unit_factor, precision_rounding=rounding)
                    move._generate_consumed_move_line(qty_to_add)
                elif len(move._get_move_lines()) < 2:
                    move.quantity_done += float_round(quantity * move.unit_factor, precision_rounding=rounding)
                else:
                    move._set_quantity_done(quantity * move.unit_factor)
        for move in production.move_finished_ids:
            if move.product_id.tracking == 'none' and move.state not in ('done', 'cancel'):
                rounding = move.product_uom.rounding
                if move.product_id.id == production.product_id.id:
                    move.quantity_done += float_round(quantity, precision_rounding=rounding)
                elif move.unit_factor:
                    move.quantity_done += float_round(quantity * move.unit_factor, precision_rounding=rounding)
        if production.state == 'confirmed':
            production.write({
                'state': 'progress',
                'date_start': fields.Datetime.now(),
            })
        # Make Mark as Done
        if production.state == 'progress':
            production.button_mark_done()
        
    # View MO(s)
    def action_view_mo(self):
        mo_list_ref_id = self.env.ref('mrp.mrp_production_tree_view').id
        mo_form_ref_id = self.env.ref('mrp.mrp_production_form_view').id

        return {
            'name': _('Manufacturing Order'),
            'res_model': 'mrp.production',
            'res_id': self.mrp_prod_ids.ids,
            'views': [(mo_list_ref_id, 'tree'), (mo_form_ref_id, 'form')],
            'domain': [('quick_production_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form'
        }

    # Check state during unlink process
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You can only in Draft state.'))
        return super(QuickProduction, self).unlink()


class QuickSaleProductLine(models.Model):
    _name = 'quick.production.line'
    _description = "Quick Sale Product Lines"
    _order = "id"

    # Quick Sale Reference
    name = fields.Char(string="Reference", required=True, copy=False, readonly=True, index=True, default=lambda self: _('New Quick Sale'), track_visibility='onchange')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'quick.sale.product.line') or _('New')
        result = super(QuickSaleProductLine, self).create(vals)
        return result

    # Other Fields
    sequence = fields.Integer(string='Sequence', default=10)
    quick_production_id = fields.Many2one('ygen.quick.production', string="Quick Production", track_visibility='onchange')
    product_id = fields.Many2one('product.product', string='Product', change_default=True, ondelete='restrict', required=True, domain=[('type', 'in', ['product', 'consu'])])
    bom_id = fields.Many2one('mrp.bom', 'Bill of Material')

    sys_on_hand = fields.Float(string='System On Hand', digits=dp.get_precision('Product Unit of Measure'))
    to_produce = fields.Float(string='To Produce', digits=dp.get_precision('Product Unit of Measure'), required=True)
    location_id = fields.Many2one(related='quick_production_id.location_id', string='Production Location')
    
    # Update price unit
    @api.onchange('product_id')
    def _onchange_product(self):
        qty = 0.0
        for quant in self.product_id.stock_quant_ids:
            if self.location_id == quant.location_id:
                qty = quant.quantity
            else:
                qty = 0
                
        self.update({'sys_on_hand': qty})

    # Filter if same product is taken more than once
    _sql_constraints = [
        ('unique_product_id_quick_prod', 'unique (product_id, quick_production_id)', 'There are duplicate product(s) in the list !'),
    ]
