# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

import datetime

from odoo import api, fields, models, _


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    @api.depends('amount_total')
    def _compute_amount_total_words(self):
        for invoice in self:
            invoice.amount_total_words = invoice.currency_id.amount_to_text(invoice.amount_total)

    amount_total_words = fields.Char("Total (In Words)", compute="_compute_amount_total_words")
    printed_copy_count = fields.Integer(string="Copy no.", readonly=True, default=0, copy=False,
        track_visibility='onchange', help="It indicates the number of times a copy of invoice has been printed.")
    print_datetime = fields.Datetime(string='Printed on', readonly=True, copy=False, track_visibility='onchange',
        help="It is the datetime on which original invoice is printed.")
    print_uid = fields.Many2one('res.users', string='Printed by', readonly=True, copy=False, track_visibility='onchange',
        help="It is the user who prints the original invoice.")
    date_transaction = fields.Datetime(string='Transaction Date', readonly=True, copy=False, track_visibility='onchange',
        help="It is the datetime on which transaction occurs.")
    tax_invoice_printed = fields.Boolean(readonly=True, default=False, copy=False,
        help="It indicates that the tax invoice has been printed.")   
    
    # Override
    @api.multi
    def action_invoice_open(self):
        open_invoices = super(AccountInvoice, self).action_invoice_open()
        # set transaction date
        self.write({"date_transaction": fields.Datetime().now()})
        return open_invoices

    # Override
    @api.multi
    def invoice_print(self):
        """ Print the copy of original invoice and increment the printed copy count
        """
        self.ensure_one()
        # Check if tax invoice has been printed
        # If it has been then increase the copy count
        # So, the first time tax invoice will be printed
        # And invoice will be printed. After that any prints 
        # will be counted as copy of original.
        # if self.sent and self.tax_invoice_printed:
        #     self.printed_copy_count += 1
        # else:
        #     self.write({'print_datetime':str(datetime.datetime.utcnow()), 'print_uid': self._uid})
        # if self.sent:
        #     self.tax_invoice_printed = True

        # This implementation makes Copy of Original as soon as 
        # when the first print is done
        if self.sent:
            self.printed_copy_count += 1
        else:
            self.write({'print_datetime':str(datetime.datetime.utcnow()), 'print_uid': self._uid})
        invoice = super(AccountInvoice, self).invoice_print()
        if self.sent:
            self.tax_invoice_printed = True
        return invoice
