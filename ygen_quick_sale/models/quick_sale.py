# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import Warning, ValidationError, UserError

import logging

_logger = logging.getLogger(__name__)

class QuickSale(models.Model):
    _name = 'ygen.quick.sale'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Quick Sale"
    _order = "id desc"

    # Quick Sale Reference
    name = fields.Char(string="Reference", required=True, copy=False, readonly=True, index=True, default=lambda self: _('New Quick Sale'), track_visibility='onchange')

    company_id = fields.Many2one(
        'res.company', 'Company',
        readonly=True, index=True, required=True,
        default=lambda self: self.env['res.company']._company_default_get('stock.inventory'))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'ygen.quick.sale') or _('New Quick Sale')
        
        # Check if other records are in draft or start state
        quick_sales = self.env['ygen.quick.sale'].search([])
        for qs in quick_sales:
            if qs.state in ('draft', 'start'):
                raise UserError(_('You have other quick sale(s) in draft or start state.\nMake sure they are validated first.'))
    
        result = super(QuickSale, self).create(vals)
        return result

    # Other Fields
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, change_default=True, index=True, track_visibility='onchange')
    order_id = fields.Many2one('sale.order', string='Sale Order', track_visibility='onchange', ondelete='restrict')
    
    # Stock Default Location
    @api.model
    def _default_location_id(self):
        company_user = self.env.user.company_id
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_user.id)], limit=1)
        if warehouse:
            return warehouse.lot_stock_id
        else:
            raise UserError(_('You must define a warehouse for the company: %s.') % (company_user.name))
    

    stock_location_id = fields.Many2one('stock.location', string='Location', required=True, track_visibility='onchange', domain="[('usage', '=', 'internal')]", readonly=True, default=_default_location_id)
    

    date = fields.Datetime(string='Order Date', required=True, copy=False, default=fields.Datetime.now, track_visibility='onchange')
    journal_id = fields.Many2one('account.journal', string='Payment Journal', domain=[('type', 'in', ('bank', 'cash'))], default=lambda self: self.env['account.journal'].search([('type', '=', 'cash')], limit=1), track_visibility='onchange')
    quick_sale_tmpl_id = fields.Many2one('ygen.quick.sale.template', string="Sale Template", track_visibility='onchange')
    product_line_ids = fields.One2many('quick.sale.product.line', 'quick_sale_id', string="Product Lines", track_visibility='onchange')
    quant_ids = fields.One2many(related="stock_location_id.quant_ids")

    # Get values from the template
    @api.onchange('quick_sale_tmpl_id')
    def on_change_template(self):
        if not self.quick_sale_tmpl_id:
            return
        
        template = self.quick_sale_tmpl_id.with_context(lang=self.partner_id.lang)
        template.refresh_on_hand()
        self.journal_id = template.journal_id
        self.partner_id = template.partner_id
        self.get_template_product_lines(template)

    # Start sale
    state = fields.Selection(string='Status', selection=[
        ('draft', 'Draft'),
        ('start', 'Start Sale'),
        ('validate', 'Validate')],
        copy=False, index=True, readonly=True,
        default='draft', track_visibility='onchange')

    # Get Template
    def get_template_product_lines(self, template):
        if template:
            product_lines = [(5, 0, 0)]
            for line in template.product_line_ids:
                if line.sys_on_hand > 0:
                    data = {
                        'quick_sale_id':self.id,
                        'sequence': line.sequence,
                        'product_id': line.product_id,
                        'real_on_hand': 0.0,
                        'sys_on_hand': line.sys_on_hand,
                        'unit_price': line.unit_price
                    }
                    product_lines.append((0, 0, data))
            self.product_line_ids = product_lines

    def action_start(self):
        for sale in self.filtered(lambda x: x.state == 'draft'):
            vals = {
                'state': 'start', 
                'date': fields.Datetime.now()
            }
            sale.write(vals)
            if not self.product_line_ids:
                sale.quick_sale_tmpl_id.refresh_on_hand()
                sale.get_template_product_lines(sale.quick_sale_tmpl_id)
        return True
    
    def action_cancel(self):
        for sale in self.filtered(lambda x: x.state not in ('draft', 'validate')):
            vals = {
                'state': 'draft', 
                'date': fields.Datetime.now(),
                'product_line_ids': [(5, 0, 0)]
            }
            sale.write(vals)
        return True
    
    # Create and Confirm Sale Order
    @api.multi
    def _prepare_order(self):
        """
        Prepare the dict of values to create the new order for a new order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        order_vals = {
            'partner_id': self.partner_id.id,
            'date_order': self.date,
            'requested_date': self.date,
            'company_id': self.company_id.id,
        }
        return order_vals
    
    def action_validate(self):
        
        # Create Sale Order and Confirm it 
        if not self.order_id:
            SaleOrder = self.env['sale.order']
            sale_order = SaleOrder.create(self._prepare_order())
            self.order_id = sale_order
            
            # Create orderline
            Product = self.env['product.product']

            for productline in self.product_line_ids:
                if productline.sys_on_hand > 0:
                    product = Product.search([('id', '=', productline.product_id.id)])
                    data = {
                        'product_id': product.id,
                        'name': product.name,
                        'price_unit': productline.unit_price or 0,
                        'product_uom_qty': productline.sold_qty,
                        'product_uom': product.uom_id.id,
                        'uom_name': product.uom_id.name
                    }
                    self.order_id.write({'order_line': [(0, 0, data)]})
        
            # Confirm Sale order with selected location
            self.order_id.action_confirm()


        for sale in self.filtered(lambda x: x.state == 'start'):
            vals = {
                'state': 'validate', 
                'date': fields.Datetime.now(),
            }
            sale.write(vals)
        
        # Sale order form view reference
        sale_order_form_ref_id = self.env.ref('sale.view_order_form').id

        # Show sale order form view
        return {
            'name': _('Sale Order'),
            'res_model': 'sale.order',
            'res_id': self.order_id.id,
            'views': [(sale_order_form_ref_id, 'form')],
            'type': 'ir.actions.act_window'
        }
    
    # Fields necessary for sale
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True)

    # Compute total price
    @api.depends('product_line_ids', 'quick_sale_tmpl_id', 'stock_location_id')
    def _compute_amount(self):
        for sale in self:
            if sale.product_line_ids:
                for line in sale.product_line_ids:
                    sale.price_total += line.amount

    # Check state during unlink process
    @api.multi
    def unlink(self):
        for sale in self:
            if sale.state != 'draft':
                raise UserError(_('You can only in Draft state.'))
        return super(QuickSale, self).unlink()


class QuickSaleProductLine(models.Model):
    _name = 'quick.sale.product.line'
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
    quick_sale_id = fields.Many2one('ygen.quick.sale', string="Quick Sale", track_visibility='onchange')
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True), ('is_addon', '=', False)], change_default=True, ondelete='restrict', required=True)

    _sql_constraints = [
        ('unique_product_id_quick_sale', 'unique (product_id, quick_sale_id)', 'There are duplicate product(s) in the list !'),
    ]

    sys_on_hand = fields.Float(string='System On Hand', digits=dp.get_precision('Product Unit of Measure'))
    real_on_hand = fields.Float(string='Real On Hand', digits=dp.get_precision('Product Unit of Measure'), required=True)
    sold_qty = fields.Float(string='Sold Qty', digits=dp.get_precision('Product Unit of Measure'), required=True, compute="_get_sold_qty")
    stock_location_id = fields.Many2one(related='quick_sale_id.stock_location_id', string='Sale Location')
    unit_price = fields.Float('Unit Price', digits=dp.get_precision('Product Price'))
    amount = fields.Float(string='Amount', compute="_compute_amount")
    
    # Update price unit
    @api.onchange('product_id')
    def _onchange_product(self):
        qty = 0.0
        for quant in self.product_id.stock_quant_ids:
            if self.stock_location_id == quant.location_id:
                qty = quant.quantity
            else:
                qty = 0
                
        self.update({
            'unit_price': self.product_id.list_price,
            'sys_on_hand': qty
        })
    
    # Compute amount of each line
    @api.depends('sold_qty', 'unit_price')
    def _compute_amount(self):
        for line in self:
            if line.sold_qty and line.unit_price:
                line.amount = line.sold_qty * line.unit_price
            else:
                line.amount = 0.0

    # Compute Sold Qty
    @api.multi
    @api.depends('product_id', 'real_on_hand')
    def _get_sold_qty(self):
        for line in self:
            if (line.sys_on_hand > 0) and (line.real_on_hand > line.sys_on_hand):
                raise UserError(_("Quantity seems greater than in the system."))
            if (line.sys_on_hand > 0) and (line.real_on_hand < 0):
                raise UserError(_("Quantity should not be negative."))
            
            if line.real_on_hand == 0:
                line.sold_qty = line.sys_on_hand
            else:
                line.sold_qty = line.sys_on_hand - line.real_on_hand

            if line.sys_on_hand <= 0:
                raise UserError(_("You have selected the product(s) whose system on hand is less or equal to zero\nPlease remove that product(s)."))
