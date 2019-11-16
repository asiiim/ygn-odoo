# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, api, _
from odoo.exceptions import Warning, ValidationError, UserError

import logging

_logger = logging.getLogger(__name__)


class SaleChangeAdvance(models.TransientModel):
    _name = 'sale.change.advance'

    so_id = fields.Many2one('sale.order', string="Sale Order")
    partner_id = fields.Many2one('res.partner', related='so_id.partner_id',readonly=True)
    adv_amount = fields.Float(string='New Advance Amount', required=True, default=0)
    journal_id = fields.Many2one('account.journal', string='Payment Journal', domain=[('type', 'in', ('bank', 'cash'))], default=lambda self: self.env['account.journal'].search([('type', '=', 'cash')], limit=1))
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    payment_id = fields.Many2one(comodel_name='account.payment', domain=[('payment_type', '=', 'inbound'),('state','in',('sent','posted'))], string="Advance Payment")
    add_advance = fields.Boolean(string='Advance', readonly=True, default=False)

    @api.multi
    def _prepare_payment(self):
        """
        Prepare the dict of values to create the new payment for a advance payment.
        """
        self.ensure_one()
        payment_methods = self.journal_id.inbound_payment_method_ids
        payment_method_id = payment_methods and payment_methods[0] or False
        payment_vals = {
            'payment_method_id': payment_method_id.id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.so_id.partner_id.id,
            'amount': self.adv_amount,
            'journal_id': self.journal_id.id,
            'payment_date': self.payment_date,
            'communication': 'New Advance Payement for order no %s' % self.so_id.name,
            'company_id': self.company_id.id,
        }
        return payment_vals

    @api.multi
    def change_advance(self):
        # Check if advance payment is greater than the total amount
        if self.adv_amount and self.adv_amount > self.so_id.amount_total:
            raise UserError(_("The Advance Amount exceeds the Total Amount.\nMake it equal to Total Amount !"))

        # Return the advance amount
        if self.so_id.payment_id:
            return_payment = self.so_id.cancel_advance_payment()

        # Check if the advance payment has been selected in payment_id
        if self.payment_id:
            payment = self.payment_id
        else:
            _logger.warning("Else Inside payment")
            Payment = self.env['account.payment']
            payment = Payment.create(self._prepare_payment())
            payment.post()
        # Assign new payment
        self.so_id.payment_id = payment
        # Open payment matching screen if it was edit advance
        if not self.add_advance:
            return return_payment
