# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class KitchenOrderNotes(models.Model):
    _name = "kitchen.order.notes"
    _description = 'Kitchen Order Notes'
    _order = 'sequence, id'
    
    sequence = fields.Integer(string="Sequence")
    name = fields.Char(string="Note")
