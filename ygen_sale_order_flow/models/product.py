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
            order_configurator_view_id = self.env.ref('ygen_sale_order_flow.ygen_order_now_form').id
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'ygen.order.now',
                'name': "Order Configurator",
                'view_mode': 'form',
                'view_id': order_configurator_view_id,
                'target': 'new',
                'context': dict(
                    self.env.context,
                    default_prd_tmpl_id=self.id,
                    default_prd_id=self.product_variant_id.id,
                    wizard_model='ygen.order.now'
                ),
            }
        return

    # This field is used to check if the product is addon
    is_addon = fields.Boolean('Is Addon', default=False, track_visibility='onchange')

    is_extra = fields.Boolean('Is Extra', default=False, track_visibility='onchange')
    is_custom = fields.Boolean('Is Custom', default=False, track_visibility='onchange')
    has_attr = fields.Boolean('Has Attribute', compute="_has_attribute", track_visibility='onchange')


    # Set true if the product template has attributes
    @api.depends('attribute_line_ids')
    def _has_attribute(self):
        for product in self:
            if len(product.attribute_line_ids) > 0:
                product.has_attr = True

    # Reference for "order now"
    @api.multi
    def action_reference_order(self):
        order_configurator_view_id = self.env.ref('ygen_sale_order_flow.ygen_order_now_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ygen.order.now',
            'name': "Order Configurator",
            'view_mode': 'form',
            'view_id': order_configurator_view_id,
            'target': 'new',
            'context': dict(
                self.env.context,
                default_ref_product_id=self.id,
                wizard_model='ygen.order.now'
            ),
        }
