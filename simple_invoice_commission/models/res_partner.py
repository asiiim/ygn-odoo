# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class InvoiceCommission(models.Model):
    _inherit = 'res.partner'
    
    commission= fields.Float(string='Commission Rate(%)')
    