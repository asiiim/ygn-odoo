# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)

class Location(models.Model):
    _inherit = 'stock.location'


    meter_reading = fields.Float(string="Meter Reading")
    shrinkage_value = fields.Float(string="Shrinkage Value")
    product_ids = fields.Many2many('product.template', 'stock_station_product', 'station_id', 'product_id', 'Products')
    product_quantity = fields.Float(related="quant_ids.quantity", string="On Hand")
