# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource

from . import kitchen_order_stage

import logging

_logger = logging.getLogger(__name__)

class KitchenOrder(models.Model):
    _name = "kitchen_order.kitchen_order"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Kitchen Order"
    _order = "priority desc, sequence, id desc"

    name = fields.Char(string="Kitchen Order Reference", required=True, copy=False, readonly=True, states={'new': [('readonly', False)]}, index=True, default=lambda self: _('New'), track_visibility='onchange')
    sequence = fields.Integer(help='Kitchen order sequence', track_visibility='onchange')
    product_id = fields.Many2one('product.product', string="Ordered Product", track_visibility='onchange')
    saleorder_id = fields.Many2one('sale.order', string="Sale Order", track_visibility='onchange')

    product_description = fields.Text(related="product_id.description", string="Product Details")
    order_description = fields.Text(string="Order Description", track_visibility='onchange')
    ko_note = fields.Text(string="Note/Content for the Order", track_visibility='onchange')

    image = fields.Binary("Image", attachment=True, track_visibility='onchange')
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Very High'),
        ], default='0', index=True, string="Priority")
            
    @api.onchange('product_id')
    def _get_product_image(self):
        for rec in self:
            if rec.product_id.image_medium:
                rec.image = rec.product_id.image_medium
    
    state = fields.Selection([
        ('new', 'New Order'),
        ('in_progress', 'In Progress'),
        ('done', 'Done To Refrigerator'),
        ('cancel', 'Order Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='new')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('kitchen_order.kitchen_order') or _('New')
        result = super(KitchenOrder, self).create(vals)
        return result