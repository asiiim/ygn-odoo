# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class SealType(models.Model):
    _name = 'seal.type'
    _order = "sequence, name"

    name = fields.Char("Name")
    sequence = fields.Integer("Sequence")
    is_master = fields.Boolean("Master Seal?", default=False)



