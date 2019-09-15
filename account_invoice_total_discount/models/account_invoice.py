# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    amount_discount_total = fields.Monetary(string='Total Discount', store=True, readonly=True, 
        compute='_compute_discount_total', track_visibility='always')

    #Compute the total discount
    @api.depends('invoice_line_ids.quantity','invoice_line_ids.price_unit','invoice_line_ids.discount','invoice_line_ids.price_subtotal')
    def _compute_discount_total(self):
        for inv in self:
            inv.amount_discount_total = sum((line.price_subtotal / (1 - (line.discount or 0.0) / 100)) - line.price_subtotal for line in inv.invoice_line_ids)
            # total_discount_amount = 0.0 
            # for line in invoice.invoice_line_ids:
            #     discount_amount = (line.quantity * line.price_unit) - line.price_subtotal
            #     total_discount_amount += discount_amount if discount_amount else 0
            # invoice.write({'amount_discount_total':total_discount_amount})