# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.addons import decimal_precision as dp

class SaleProductLine(models.Model):
    _name = 'sale.product.line'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Sale Product Lines"
    _order = "id"

    # Quick Sale Reference
    name = fields.Char(string="Reference", required=True, copy=False, readonly=True, index=True, default=lambda self: _('New Quick Sale'), track_visibility='onchange')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'sale.product.line') or _('New Product Line')
        result = super(SaleProductLine, self).create(vals)
        return result

    # Other Fields
    sequence = fields.Integer(string='Sequence', default=10)
    quick_sale_id = fields.Many2one('ygen.quick.sale', string="Quick Sale", track_visibility='onchange')
    quick_sale_tmpl_id = fields.Many2one('ygen.sale.template', string="Sale Template", track_visibility='onchange')
    order_id = fields.Many2one(related='quick_sale_id.order_id', string='Sale Order', track_visibility='onchange')
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict', required=True)
    uom_sold_qty = fields.Float(string='Sold Qty', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    on_hand_qty = fields.Float(string='On Hand', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    
    