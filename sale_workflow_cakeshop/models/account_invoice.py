# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    tender_amount = fields.Monetary(string='Tender', track_visibility='always', default=0.0)
    change_amount = fields.Monetary(string='Change', track_visibility='always', default=0.0)
