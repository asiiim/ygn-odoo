# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def action_order_now(self):
        """Return action to start order now wizard"""
        _logger.error("**************")
        return self.create_config_wizard(model_name="product.configurator.ordernow")
        # return {
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'product.configurator.ordernow',
        #     'name': "Product Configurator",
        #     'view_mode': 'form',
        #     'target': 'new',
        #     'context': dict(
        #         self.env.context,
        #         # default_order_id=self.id,
        #         default_product_tmpl_id=self.id,
        #         wizard_model='product.configurator.ordernow',
        #     ),
        # }