# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.osv import expression

class ResPartner(models.Model):
    _inherit = "res.partner"

    house_number = fields.Char('House Number')