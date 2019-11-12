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
        # Check whether product template has any variants
        if len(self.attribute_line_ids) == 0:
            order_configurator_view_id = self.env.ref('sale_workflow_cakeshop.product_configurator_ordernow_ko_form').id
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'product.configurator.ordernow.ko',
                'name': "Order Configurator",
                'view_mode': 'form',
                'view_id': order_configurator_view_id,
                'target': 'new',
                'context': dict(
                    self.env.context,
                    default_product_tmpl_id=self.id,
                    default_product_id=self.product_variant_id.id,
                    wizard_model='product.configurator.ordernow.ko',
                ),
            }
        return
        # return self.create_config_wizard(model_name="product.configurator.ordernow")

    # This field is used to check if the product is addon
    is_addon = fields.Boolean('Is Addon', default=False)
    is_custom = fields.Boolean('Is Custom', default=False)
    has_attr = fields.Boolean('Has Attribute', compute="_has_attribute")

    # set true if the product template has attributes
    @api.depends('attribute_line_ids')
    def _has_attribute(self):
        for product in self:
            if len(product.attribute_line_ids) > 0:
                product.has_attr = True

class ProductProduct(models.Model):
    _inherit = "product.product"

    # This field is used to check if the product is addon
    is_addon = fields.Boolean(related="product_tmpl_id.is_addon")
    is_custom = fields.Boolean(related="product_tmpl_id.is_custom")
    has_attr = fields.Boolean('Has Attribute', related="product_tmpl_id.has_attr", store=True)
    
    product_addon_line_ids = fields.One2many('product.addons.line', 'product_id', string='Addon Lines', copy=True, auto_join=True)
