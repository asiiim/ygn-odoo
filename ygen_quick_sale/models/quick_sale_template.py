# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import Warning, ValidationError, UserError

import logging

_logger = logging.getLogger(__name__)

class QuickSaleTemplate(models.Model):
    _name = 'ygen.quick.sale.template'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Quick Sale Template"
    _order = "id"

    # Quick Sale Reference
    name = fields.Char(string="Reference", required=True, copy=False, index=True, track_visibility='onchange')

    # Other Fields
    journal_id = fields.Many2one('account.journal', string='Payment Journal', domain=[('type', 'in', ('bank', 'cash'))], default=lambda self: self.env['account.journal'].search([('type', '=', 'cash')], limit=1), track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string='Customer', change_default=True, index=True, track_visibility='onchange')
    quick_sale_ids = fields.One2many('ygen.quick.sale', 'quick_sale_tmpl_id', string="Sale Template", track_visibility='onchange')
    product_line_ids = fields.One2many('quick.sale.product.template.line', 'quick_sale_tmpl_id', string="Product Lines", track_visibility='onchange')

     # Refresh System Qty
    @api.multi
    def refresh_on_hand(self):
        for line in self.product_line_ids:
            line.refresh_sys_on_hand()

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
    


class QuickSaleProductTemplateLine(models.Model):
    _name = 'quick.sale.product.template.line'
    _description = "Quick Sale Product Template Lines"
    _order = "id"

    # Quick Sale Reference
    name = fields.Char(string="Reference", required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'), track_visibility='onchange')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'quick.sale.product.template.line') or _('New')
        result = super(QuickSaleProductTemplateLine, self).create(vals)
        return result

    # Other Fields
    sequence = fields.Integer(string='Sequence', default=10)
    quick_sale_tmpl_id = fields.Many2one('ygen.quick.sale.template', string="Quick Sale Template", track_visibility='onchange')
    
    # Ensure unique products
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True), ('is_addon', '=', False)], change_default=True, ondelete='restrict', required=True)

    _sql_constraints = [
        ('unique_product_id_template', 'unique (product_id, quick_sale_tmpl_id)', 'There are duplicate product(s) in the list !'),
    ]

    stock_location_id = fields.Many2one(related='quick_sale_tmpl_id.stock_location_id', string='Location')
    sys_on_hand = fields.Float(string='System On Hand', digits=dp.get_precision('Product Unit of Measure'), compute='_get_sys_on_hand', store=True)
    unit_price = fields.Float(related="product_id.list_price", string='Unit Price', readonly=True)

    #  Get available system on hand qty of the selected
    @api.multi
    @api.depends('product_id')
    def _get_sys_on_hand(self):
        for line in self:
            for quant in line.product_id.stock_quant_ids:
                if line.stock_location_id == quant.location_id:
                    line.sys_on_hand = quant.quantity
                else:
                    line.sys_on_hand = 0

    @api.multi
    def refresh_sys_on_hand(self):
        for rec in self:
            rec._get_sys_on_hand()
