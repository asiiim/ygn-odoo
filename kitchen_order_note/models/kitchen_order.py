# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class KitchenOrder(models.Model):
    _inherit = "kitchen.order"

    ko_notes_ids = fields.Many2many('kitchen.order.notes', 'kitchen_order_kitchen_order_notes_', string='KO Notes')
