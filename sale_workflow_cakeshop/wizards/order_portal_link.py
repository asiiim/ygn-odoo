# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _

import logging

_logger = logging.getLogger(__name__)


class OrderPortalLink(models.TransientModel):
    _name = 'order.portal.link'

    portal_link = fields.Text("Order Portal Link", readonly=True, help="Copy and share this link to the customer for the order reference.")
