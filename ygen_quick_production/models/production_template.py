# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import Warning, ValidationError, UserError

class QuickProductionTemplate(models.Model):
    _name = 'ygen.quick.production.template'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Quick Production Template"
    _order = "id"

    # Quick Sale Reference
    name = fields.Char(string="Reference", required=True, copy=False, index=True, track_visibility='onchange')
    company_id = fields.Many2one(
        'res.company', 'Company',
        readonly=True, index=True, required=True,
        default=lambda self: self.env['res.company']._company_default_get('mrp.production'))

    # Other Fields
    product_line_ids = fields.One2many('quick.production.template.line', 'quick_production_tmpl_id', string="Product Lines", track_visibility='onchange')

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

    # Refresh System Qty
    @api.multi
    def refresh_on_hand(self):
        for line in self.product_line_ids:
            line.refresh_sys_on_hand()


class QuickSaleProductTemplateLine(models.Model):
    _name = 'quick.production.template.line'
    _description = "Quick Production Template Lines"
    _order = "id"

    # Quick Sale Reference
    name = fields.Char(string="Reference", required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'), track_visibility='onchange')
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'quick.production.template.line') or _('New')
        result = super(QuickSaleProductTemplateLine, self).create(vals)
        return result

    # Other Fields
    sequence = fields.Integer(string='Sequence', default=10)
    quick_production_tmpl_id = fields.Many2one('ygen.quick.production.template', string="Quick Production Template")
    product_id = fields.Many2one('product.product', string='Product', change_default=True, ondelete='restrict', required=True, domain=[('type', 'in', ['product', 'consu'])])
    bom_id = fields.Many2one('mrp.bom', 'Bill of Material')

    location_id = fields.Many2one(related='quick_production_tmpl_id.location_id', string='Location')
    sys_on_hand = fields.Float(string='System On Hand', digits=dp.get_precision('Product Unit of Measure'), compute='_get_sys_on_hand')

    #  Get available system on hand qty of the selected
    @api.multi
    @api.depends('product_id', 'location_id')
    def _get_sys_on_hand(self):
        for line in self:
            for quant in line.product_id.stock_quant_ids:
                if line.location_id == quant.location_id:
                    line.sys_on_hand = quant.quantity
                    break
                else:
                    line.sys_on_hand = 0

    # Refresh System Qty
    @api.multi
    def refresh_sys_on_hand(self):
        for rec in self:
            rec._get_sys_on_hand()

    # Filter if same product is taken more than once
    _sql_constraints = [
        ('unique_product_id_quick_prod_tmpl', 'unique (product_id, quick_production_tmpl_id)', 'There are duplicate product(s) in the list !'),
    ]
