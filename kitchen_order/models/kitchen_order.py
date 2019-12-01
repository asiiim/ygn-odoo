# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

import time

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

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
    _order = "requested_date, priority desc, id"

    name = fields.Char(string="Kitchen Order Reference", required=True, copy=False,
                       readonly=True, index=True, default=lambda self: _('New'), track_visibility='onchange')
    # sequence = fields.Integer(help='Kitchen order sequence', track_visibility='onchange')
    product_id = fields.Many2one(
        'product.product', string="Ordered Product", track_visibility='onchange')
    saleorder_id = fields.Many2one(
        'sale.order', string="Sale Order", track_visibility='onchange')
    product_description = fields.Text(
        related="product_id.description", string="Product Details")
    ko_note = fields.Text(string="Kitchen Order Note",
                          translate=True, track_visibility='onchange')
    image = fields.Binary(related="product_id.image", attachment=True,
                          track_visibility='onchange')
    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('kitchen.order'))
    date_order = fields.Datetime(
        related="saleorder_id.date_order", string="Ordered Date", track_visibility='onchange')
    requested_date = fields.Datetime(
        related="saleorder_id.requested_date", string="Delivery Date", store=True)
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision(
        'Product Unit of Measure'), readonly=1, required=True, default=1.0, track_visibility='onchange')
    uom = fields.Many2one(related="product_id.uom_id", string='Unit of Measure', readonly=1,
                          required=True, track_visibility='onchange')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'kitchen.order') or _('New')
        result = super(KitchenOrder, self).create(vals)
        return result

    # Kanban View Essentials
    active = fields.Boolean(default=True, track_visibility='onchange')
    priority = fields.Selection(kitchen_order_stage.AVAILABLE_PRIORITIES, string='Priority', index=True,
                                default=kitchen_order_stage.AVAILABLE_PRIORITIES[0][0], track_visibility='onchange')
    stage_id = fields.Many2one('kitchen.stage', string='Stage', track_visibility='onchange', index=True,
                               group_expand='_read_group_stage_ids', default=lambda self: self.env['kitchen.stage'].search([('name', '=', 'New')], limit=1))
    stage_name = fields.Char(related='stage_id.name',
                             string="Stage Name", store=True)
    # color = fields.Integer('Color Index', default=0)
    kanban_state = fields.Selection([('today', 'Ordered Requested Today'), ('delayed', 'Delayed Requested Order'), ('future', 'Future Requested Order')],
                                    string='Activity State', compute='_compute_kanban_state', copy=False, default='grey', required=True,)
    kanban_state_label = fields.Char(
        compute='_compute_kanban_state_label', string='Kanban State', track_visibility='onchange')

    legend_red = fields.Char(related='stage_id.legend_red',
                             string='Kanban Delayed Explanation', readonly=True, related_sudo=False)
    legend_green = fields.Char(related='stage_id.legend_green',
                               string='Kanban Future Explanation', readonly=True, related_sudo=False)
    legend_grey = fields.Char(related='stage_id.legend_grey',
                              string='Kanban Normal Explanation', readonly=True, related_sudo=False)

    @api.multi
    def _compute_kanban_state(self):
        today = datetime.now().strftime('%Y-%m-%d')
        for order in self:
            if order.requested_date:
                order_req_date = fields.Datetime.from_string(
                    order.requested_date).strftime('%Y-%m-%d')
                if order_req_date == today:
                    kanban_state = 'today'
                elif order_req_date > today:
                    kanban_state = 'future'
                else:
                    kanban_state = 'delayed'
            order.kanban_state = kanban_state

    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for order in self:
            if order.kanban_state == 'today':
                order.kanban_state_label = order.legend_grey
            elif order.kanban_state == 'delayed':
                order.kanban_state_label = order.legend_red
            else:
                order.kanban_state_label = order.legend_green

    @api.multi
    def cancel_kitchen_order(self):
        self.ensure_one()
        for rec in self:
            rec.write({
                'stage_id': self.env['kitchen.stage'].search([('name', '=', 'Cancel')], limit=1).id
            })

    @api.multi
    def start_kitchen_order(self):
        self.ensure_one()
        for rec in self:
            rec.write({
                'stage_id': self.env['kitchen.stage'].search([('name', '=', 'In Progress')], limit=1).id
            })

    @api.multi
    def finish_kitchen_order(self):
        self.ensure_one()
        for rec in self:
            rec.write({
                'stage_id': self.env['kitchen.stage'].search([('name', '=', 'Done')], limit=1).id
            })

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['kitchen.stage'].search([])
        for stage in stage_ids:
            if stage.name == "Cancel":
                stage.fold = True
        return stage_ids

    # Report Section
    @api.multi
    def print_kitchen_order(self):
        return self.env.ref('kitchen_order.action_report_kitchen_order').report_action(self)

    # Kitchen Order Message
    message_id = fields.Many2one(
        'kitchen.message', string="Message", track_visibility='onchange')
    related_template_message = fields.Char(related='message_id.name', string="Related Template Message")
    name_for_message = fields.Text(
        string="Name for Message", track_visibility='onchange')
    message = fields.Char(compute="_compute_order_message", 
        string="Message", track_visibility='onchange')
    
    @api.multi
    @api.depends('message_id', 'name_for_message', 'related_template_message')
    def _compute_order_message(self):
        for ko in self:
            ko.message = ko.related_template_message or 'MESSAGE NOT PROVIDED'
            ko.message += ' ' + str(ko.name_for_message)

    # Link Invoice(s) With Kitchen Order
    invoice_ids = fields.Many2many(related="saleorder_id.invoice_ids", string='Invoice Ref.')

    # Reference Product
    ref_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        domain="[('sale_ok', '=', True), ('is_custom', '=', False), ('is_addon', '=', False)]",
        track_visibility='onchange'
    )
    ref_image = fields.Binary(related='ref_product_id.image', string='Reference Image', attachment=True, track_visibility='onchange')
