# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _

import logging

_logger = logging.getLogger(__name__)


class OrderPortalLink(models.TransientModel):
    _name = 'order.portal.link'

    @api.model
    def _get_order_link(self):
        sale_order = self.env['sale.order'].browse(self._context.get('active_id', []))
        return sale_order.generate_portal_link()

    portal_link = fields.Text("Order Portal Link", default=_get_order_link, readonly=True, help="Copy and share this link to the customer for the order reference.")
