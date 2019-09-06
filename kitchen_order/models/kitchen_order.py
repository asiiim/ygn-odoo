# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource
from datetime import datetime, timedelta, date
from odoo.addons import decimal_precision as dp

from . import kitchen_order_stage

import logging

_logger = logging.getLogger(__name__)

class KitchenOrder(models.Model):
    _name = "kitchen.order"
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
    image = fields.Binary("Image", attachment=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('kitchen.order'))
    date_order  = fields.Datetime(related="saleorder_id.date_order", string="Ordered Date", track_visibility='onchange')    
    requested_date  = fields.Datetime(related="saleorder_id.requested_date", string="Order Requested Date", track_visibility='onchange')
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), readonly=1, required=True, default=1.0, track_visibility='always')
            
    @api.onchange('product_id')
    def _get_product_image(self):
        for rec in self:
            if rec.product_id.image_medium:
                rec.image = rec.product_id.image_medium

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('kitchen.order') or _('New')
        result = super(KitchenOrder, self).create(vals)
        return result

    # Kanban View Essentials
    active = fields.Boolean(default=True, track_visibility='onchange')
    priority = fields.Selection(kitchen_order_stage.AVAILABLE_PRIORITIES, string='Priority', index=True, default=kitchen_order_stage.AVAILABLE_PRIORITIES[0][0], track_visibility='onchange')
    stage_id = fields.Many2one('kitchen.stage', string='Stage', track_visibility='onchange', index=True, group_expand='_read_group_stage_ids', default=lambda self: self.env['kitchen.stage'].search([('name', '=', 'New')], limit=1))
    color = fields.Integer('Color Index', default=0)

    @api.multi
    def cancel_kitchen_order(self):
        self.ensure_one()
        for rec in self:
            rec.write({
                'stage_id': self.env['kitchen.stage'].search([('name', '=', 'Cancel')], limit=1).id
            })

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['kitchen.stage'].search([])
        for stage in stage_ids:
            if stage.name == "Cancel":
                stage.fold = True
        return stage_ids
