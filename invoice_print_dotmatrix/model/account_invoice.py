# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

import datetime

from odoo import api, fields, models, _


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    # Override
    @api.multi
    def invoice_print(self):
        """ Print the copy of original invoice and increment the printed copy count
        """
        self.ensure_one()
        invoice = super(AccountInvoice, self).invoice_print()
        return self.env.ref('invoice_print_dotmatrix.account_invoices_dot_matrix').report_action(self)
