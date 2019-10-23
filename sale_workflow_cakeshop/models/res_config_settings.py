# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

import json
import logging
import requests
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_order_report = fields.Many2one(related="company_id.sale_order_report", string="Sale Order Report")
    kitchen_order_report = fields.Many2one(related="company_id.kitchen_order_report", string="Kitchen Order Report")
