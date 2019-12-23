# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models


class MrpBomLine(models.Model):
    _inherit = ['mrp.bom.line', 'product.configurator']
    _name = 'mrp.bom.line'
