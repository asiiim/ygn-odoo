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

    # Override
    @api.multi
    def invoice_print(self):
        """ Print the copy of original invoice and increment the printed copy count
        """
        self.ensure_one()
        if self.sent:
            self.printed_copy_count += 1
        else:
            self.write({'print_datetime':str(datetime.datetime.utcnow()), 'print_uid': self._uid})
        return super(AccountInvoice, self).invoice_print()
