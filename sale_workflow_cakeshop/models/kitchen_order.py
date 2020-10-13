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
        new_order_configurator_view_id = self.env.ref('sale_workflow_cakeshop.product_configurator_ordernow_ko_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.configurator.ordernow.ko',
            'name': "New Order Configurator",
            'view_mode': 'form',
            'view_id': new_order_configurator_view_id,
            'target': 'new',
            'context': dict(
                self.env.context,
                wizard_model='product.configurator.ordernow.ko'
            )
        }
    
    # Order again
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
        return self.env.ref('sale_workflow_cakeshop.action_report_sale_or_kitchen_order').report_action(self.saleorder_id)

    # Portal SO or KO
    @api.multi
    def share_portal_link(self):
        return self.saleorder_id.share_portal_link()
