# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import Warning, ValidationError, UserError

import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    kitchen_order_ids = fields.One2many(
        comodel_name='kitchen.order',
        inverse_name='saleorder_id',
        string="Kitchen Orders",
        track_visibility='onchange'
    )
    
    # Check if SO has KO
    has_ko = fields.Boolean(compute="_has_kitchen_orders", string="Has Kitchen Order(s)")
    @api.depends('kitchen_order_ids')
    def _has_kitchen_orders(self):
        for order in self:
            if len(order.kitchen_order_ids) > 0:
                order.has_ko = True
            else:
                order.has_ko = False

    # Print option selection for KO & SO
    kitchen_sale_order_print_selection = fields.Selection([('ko', 'Kitchen Order'), ('so', 'Sale Order'), ('both', 'Both')], string="Print Sale Order or Kitchen Order?", default="both")

    # Print SO or KO
    @api.multi
    def print_koso_report(self):
        self.ensure_one()
        return self.env.ref('ygen_sale_kitchen_workflow.action_report_sale_or_kitchen_order').report_action(self)

    # View related kitchen orders of the sale order
    @api.multi
    def view_kitchen_order(self):
        self.ensure_one()
        # return list view action if there are more than one KOs, or 
        # return form view if there is only one ko else return tree view
        action = {
            'name': _('Kitchen Order'),
            'res_model': 'kitchen.order',
            'views': [(self.env.ref('kitchen_order.view_kitchen_order_tree').id, 'tree')],
            'type': 'ir.actions.act_window',
            'target':'new'
        }

        kitchen_orders = self.mapped('kitchen_order_ids')
        if len(kitchen_orders) > 1:
            action['domain'] = [('id', 'in', kitchen_orders.ids)]
        elif kitchen_orders:
            action['views'] = [(self.env.ref('kitchen_order.view_kitchen_order_form').id, 'form')]
            action['res_id'] = kitchen_orders.id
        return action

    # Cancel Kitchen Orders, Delivery and Advance if SO is Cancelled
    @api.multi
    def action_cancel(self):
        kitchen_orders = self.mapped('kitchen_order_ids')
        # Cancel Kitchen Orders
        kitchen_orders.cancel_kitchen_order()
        return super(SaleOrder, self).action_cancel()

    # Essential fields for sale order tree view
    delivery_status = fields.Boolean('Delivery Status', default=False, copy=False, track_visibility='onchange')
    ko_status = fields.Boolean('KO Status', default=False, copy=False, track_visibility='onchange')

    @api.multi
    def set_ko_ready(self):
        for rec in self:
            rec.write({'ko_status': True})

    @api.multi
    def dispatch_so(self):
        for rec in self:
            rec.write({
                'ko_status': True,
                'delivery_status': True
                })
 
    ko_message = fields.Text('KO Message', compute="_get_ko_message", track_visibility='onchange')

    @api.depends('kitchen_order_ids')
    def _get_ko_message(self):
        for record in self:
            msg = ""
            for ko in record.kitchen_order_ids:
                msg = msg + ko.name_for_message
            record['ko_message'] = msg

    customer_street = fields.Char('Street', related="partner_shipping_id.street", track_visibility='onchange')

