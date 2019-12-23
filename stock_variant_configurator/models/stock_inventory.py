# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models


class InventoryLine(models.Model):
    _inherit = ['stock.inventory.line', 'product.configurator']
    _name = 'stock.inventory.line'
