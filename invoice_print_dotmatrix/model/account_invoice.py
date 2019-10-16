# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

import datetime

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    # Override
    @api.multi
    def invoice_print(self):
        """ Print the copy of original invoice and increment the printed copy count
        """
        self.ensure_one()
        
        report_ref = self.env.ref('invoice_print_dotmatrix.account_invoices_dot_matrix')
        report_ref.write({'direct_print': True})

        invoice = super(AccountInvoice, self).invoice_print()
        return report_ref.report_action(self)
