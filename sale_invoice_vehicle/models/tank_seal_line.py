# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class SealLine(models.Model):
    _inherit = 'seal.line'
    
    invoice_id = fields.Many2one('account.invoice', string='Invoice Reference', ondelete='cascade', index=True)