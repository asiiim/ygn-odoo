# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class KitchenOrder(models.Model):
    _inherit = "kitchen.order"

    so_ref = fields.Char(related='saleorder_id.name', string='Sale Order')

    # Order again
    @api.multi
    def new_order(self):
        self.ensure_one()
        new_order_configurator_view_id = self.env.ref('ygen_sale_order_flow.ygen_order_now_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ygen.order.now',
            'name': "New Order Configurator",
            'view_mode': 'form',
            'view_id': new_order_configurator_view_id,
            'target': 'new',
            'context': dict(
                self.env.context,
                wizard_model='ygen.order.now'
            )
        }
    
    # View Order
    @api.multi
    def view_order(self):
        self.ensure_one()
        sale_order_form_ref_id = self.env.ref('sale.view_order_form').id
        return {
            'name': _('Sale Order'),
            'res_model': 'sale.order',
            'res_id': self.saleorder_id.id,
            'views': [(sale_order_form_ref_id, 'form')],
            'type': 'ir.actions.act_window'
        }

    # Print SO or KO
    @api.multi
    def print_soko_report(self):
        self.ensure_one()
        return self.env.ref('ygen_sale_kitchen_workflow.action_report_sale_or_kitchen_order').report_action(self.saleorder_id)