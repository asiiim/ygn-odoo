# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class KitchenOrder(models.Model):
    _inherit = "kitchen.order"

    drive_file_ids = fields.Many2many('drive.file', 'kitchen_order_drive_file_uri_', string='Reference Files')