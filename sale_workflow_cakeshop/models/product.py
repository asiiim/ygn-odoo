# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def action_order_now(self):
        """Return action to start order now wizard"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.configurator.ordernow',
            'name': "Order Configurator",
            'view_mode': 'form',
            'target': 'new',
            'context': dict(
                self.env.context,
                default_order_id=self.id,
                wizard_model='product.configurator.ordernow',
            ),
        }