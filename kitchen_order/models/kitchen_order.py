# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource
from datetime import datetime, timedelta, date

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
    requested_date  = fields.Datetime(related="saleorder_id.requested_date", string="Order Requested Date")
            
    @api.onchange('product_id')
    def _get_product_image(self):
        for rec in self:
            if rec.product_id.image_medium:
                rec.image = rec.product_id.image_medium

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('kitchen_order.kitchen_order') or _('New')
        result = super(KitchenOrder, self).create(vals)
        return result

    # Kanban View Essentials
    ################################## [ Work in Progress ] #############################################################################
    active = fields.Boolean(default=True)
    priority = fields.Selection(kitchen_order_stage.AVAILABLE_PRIORITIES, string='Priority', index=True, default=kitchen_order_stage.AVAILABLE_PRIORITIES[0][0])
    stage_id = fields.Many2one('kitchen_order.stage', string='Stage', track_visibility='onchange', index=True, group_expand='_read_group_stage_ids')
    color = fields.Integer('Color Index', default=0)

    @api.multi
    def cancel_kitchen_order(self):
        self.ensure_one()
        for rec in self:
            rec.write({
                'active': False
            })

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        # retrieve team_id from the context and write the domain
        # - ('id', 'in', stages.ids): add columns that should be present
        # - OR ('fold', '=', False): add default columns that are not folded
        
        search_domain = [('id', 'in', stages.ids)]

        # perform search
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)