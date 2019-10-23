# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.
import base64
import os
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError


class Company(models.Model):
    _inherit = "res.company"

    sale_order_report = fields.Many2one('ir.actions.report', string="Sale Order Report", domain="[('model', '=', 'sale.order')]")
    kitchen_order_report = fields.Many2one('ir.actions.report', string="Kitchen Order Report", domain="[('model', '=', 'kitchen.order')]")
