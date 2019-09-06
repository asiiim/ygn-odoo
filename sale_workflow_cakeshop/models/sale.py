# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "sale.order"

    kitchen_order_ids = fields.One2many(
        comodel_name='kitchen.order',
        inverse_name='saleorder_id',
        string="Kitchen Orders"
    )

    