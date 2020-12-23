# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _

import logging

_logger = logging.getLogger(__name__)


class KitchenOrder(models.Model):
    _inherit = "kitchen.order"

    custom_image = fields.Binary(
        "Custom Image",
        help="This field holds the custom image for the kitchen order.")

    secondary_custom_image = fields.Binary(
        "Secondary Custom Image",
        help="This field holds the secondary custom image for the kitchen order.")

    flush_custom_images = fields.Boolean("To Flush Images", default=False)
    

    @api.multi
    def action_zoom_ko(self):
        """
        Zooms the current kitchen order showing custom images provided by the client.
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kitchen.order',
            'name': self.name,
            'res_id': self.id,
            'views': [(self.env.ref('kitchen_order_summary.ko_zoom_view').id, 'form')],
            'target': 'new',
            'context': dict(
                self.env.context,
            ),
        }

    @api.multi
    def action_view_ko_summary(self):
        """
        View current kitchen order summary.
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kitchen.order',
            'name': self.name,
            'res_id': self.id,
            'views': [(self.env.ref('kitchen_order_summary.ko_summarized_view').id, 'form')],
            'target': 'new',
            'context': dict(
                self.env.context,
            ),
        }