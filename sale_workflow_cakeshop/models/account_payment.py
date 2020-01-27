# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class account_payment(models.Model):
    _inherit = 'account.payment'

    move_reconciled = fields.Boolean(compute="_get_move_reconciled", readonly=True, store=True)
    sale_id = fields.Many2one('sale.order', 'Related Sale Order')

