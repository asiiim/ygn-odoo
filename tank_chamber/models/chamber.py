# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class TankChamber(models.Model):
    _name = 'chamber.chamber'
    _order = "sequence, name"

    name = fields.Integer("Name")
    
    sequence = fields.Integer("Sequence")

    _sql_constraints = [('unique_chamber', 'unique (name)', 'You can not have two same chambers!')]