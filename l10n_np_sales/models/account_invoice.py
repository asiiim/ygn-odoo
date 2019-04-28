# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

import datetime
import logging
import json
import threading

import requests

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError
from odoo import tools

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    amount_export = fields.Monetary(string='Export Sales',
        store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    amount_non_taxable = fields.Monetary(string='Non Taxable Sales',
        store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    amount_taxable = fields.Monetary(string='Taxable Sales Amount',
        store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    
    # Override
    @api.multi
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice')
    def _compute_amount(self):
        super(AccountInvoice, self)._compute_amount()
        for inv in self:
            inv.amount_taxable = sum(line.price_subtotal if len(line.invoice_line_tax_ids.ids) > 0 else 0 for line in inv.invoice_line_ids)
            inv.amount_non_taxable = inv.amount_untaxed - inv.amount_taxable
            # compute export sales
            export_sales_tag = inv.env.ref('l10n_np.tax_tag_export')
            vat_group = inv.env.ref('l10n_np.tax_group_tax_vat')
            inv.amount_export = sum(line.base if (export_sales_tag.id in line.tax_id.tag_ids.ids and line.tax_id.tax_group_id.id == vat_group.id) else 0.0 for line in inv.tax_line_ids)
