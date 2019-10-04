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

    tender_amount = fields.Float(string='Tender', default=0.0)
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

        # validate the invoice
        for record in self.env['account.invoice'].search([('origin', '=', str(order.name))]):
            if record.state != 'draft':
                raise UserError(_("Selected invoice(s) cannot be confirmed as they are not in 'Draft' state."))
            record.action_invoice_open()
        
        # register the payment
        advance_payment = self.env['account.payment'].search([('id', '=', order.payment_id.id)])
        credit_aml = advance_payment.move_line_ids.filtered(lambda aml: aml.credit > 0)

        invoice = order.invoice_ids.filtered(lambda inv: inv.amount_total_signed > 0)
        invoice.assign_outstanding_credit(credit_aml.id)

        journal = self.env['account.journal'].search([('type', '=', 'cash')], limit=1)
        payment_methods = journal.inbound_payment_method_ids
        payment_method_id = payment_methods and payment_methods[0] or False

        payment_vals = {
            'payment_method_id': payment_method_id.id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': order.partner_id.id,
            'amount': self.total_due_amount,
            'journal_id': journal.id,
            'payment_date': self.payment_date,
            'communication': 'Total Due Payement for order no %s' % order.name,
            'company_id': order.company_id.id,
            'invoice_ids': [(4, invoice.id)]
        }

        payment_obj = self.env['account.payment']
        payment = payment_obj.create(payment_vals)
        payment.post()
        self.payment_id = payment

