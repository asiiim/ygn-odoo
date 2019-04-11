# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    max_shrinkage_loss = fields.Float(string='Maximum Shrinking Loss', default=0.0)
