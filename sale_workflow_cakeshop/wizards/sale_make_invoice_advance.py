# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    # take tender amount
    tender_amount = fields.Float(string='Tender', compute="_take_tender")
    tender_amount_char = fields.Char(string="Tender")
    journal_id = fields.Many2one('account.journal', string='Payment Journal', domain=[('type', 'in', ('bank', 'cash'))], default=lambda self: self.env['account.journal'].search([('type', '=', 'cash')], limit=1))

    @api.depends('tender_amount_char')
    def _take_tender(self):
        try:
            self.tender_amount = float(self.tender_amount_char)
        except:
            raise UserError(_("Plese enter number NOT text!"))

    change_amount = fields.Float(string='Change', default=0.0, compute="_get_change")
    total_due_amount = fields.Float(string='Total Due Amount', default=0.0, compute="_get_total_amount")

    @api.depends('tender_amount', 'change_amount')
    def _get_total_amount(self):
        sale_obj = self.env['sale.order']
        order = sale_obj.browse(self._context.get('active_ids'))[0]
        self.total_due_amount = order.amount_due

    @api.depends('tender_amount')
    def _get_change(self):

        if self.tender_amount and self.tender_amount > self.total_due_amount:
            self.change_amount = self.tender_amount - self.total_due_amount
        else:
            self.change_amount = 0.0

    # Register Payment of Due Amount
    payment_id = fields.Many2one(
        comodel_name='account.payment',
        readonly=True
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        readonly=False,
        string="Customer"
    )
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)

    @api.multi
    def pay_bill(self):
        
        self.ensure_one()

        # create the invoice
        sale_obj = self.env['sale.order']
        order = sale_obj.browse(self._context.get('active_ids'))[0]
        order.write({
            'tender_amount': self.tender_amount,
            'change_amount': self.change_amount
        })
        self.create_invoices()
        invoice = order.invoice_ids.filtered(lambda inv: inv.amount_total_signed > 0 and inv.state == 'draft')[0]
        
        if invoice and not invoice.action_invoice_open():
            raise UserError(_("Invoice could not be validated, you can review them before validation."))
        
        # Reconcile advance payment
        if order.payment_id:
            
            # Post the draft advance payment:
            if order.payment_id.state == "draft":
                order.payment_id.post()
            
            credit_aml = order.payment_id.move_line_ids.filtered(lambda aml: aml.credit > 0)
            invoice.assign_outstanding_credit(credit_aml.id)

        # Register the payment
        if self.total_due_amount > 0.0:
            payment_methods = self.journal_id.inbound_payment_method_ids
            payment_method_id = payment_methods and payment_methods[0] or False

            payment_vals = {
                'payment_method_id': payment_method_id.id,
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'partner_id': order.partner_id.id,
                'amount': self.total_due_amount,
                'journal_id': self.journal_id.id,
                'payment_date': self.payment_date,
                'communication': 'Total Due Payement for order no %s' % order.name,
                'company_id': order.company_id.id,
                'invoice_ids': [(4, invoice.id)]
            }

            payment_obj = self.env['account.payment']
            payment = payment_obj.create(payment_vals)
            payment.post()
            self.payment_id = payment

