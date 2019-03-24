# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    tanker_vehicle_number = fields.Char('Vehicle No.')
