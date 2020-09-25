# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, api, _
from odoo.exceptions import Warning, ValidationError, UserError

from odoo.addons import decimal_precision as dp

import logging

_logger = logging.getLogger(__name__)


class YgenOrderNow(models.TransientModel):
    _inherit = 'ygen.order.now'

    payment_id = fields.Many2one(comodel_name='account.payment', readonly=True)
    advance_amount = fields.Monetary(string='Advance Amount', required=True, default=0)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)

    @api.multi
    def _prepare_payment(self, so_amount):
        """
        Prepare the dict of values to create the new payment for a advance payment. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()

        # There might be case the total order amount may be greater than that in sale order total due to 
        # tax or fixed discount (for example: if total = 2100, and sale order total = 2099.99). In this
        # case if the advance amount is paid equal to total in wizard order, there might become the issue of
        # being negative due amount (for example: if sale order total = 2099.99, advance = 2100, then due = -0.01)
        # Below is fix for above case.
        adv_amt = 0.0
        if self.price_total == self.advance_amount:
            adv_amt = so_amount
        else:
            adv_amt = self.advance_amount

        payment_methods = self.journal_id.inbound_payment_method_ids
        payment_method_id = payment_methods and payment_methods[0] or False
        payment_vals = {
            'payment_method_id': payment_method_id.id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner_id.id,
            'amount': adv_amt,
            'journal_id': self.journal_id.id,
            'payment_date': self.payment_date,
            'communication': 'Advance Payment for order no %s' % self.order_id.name,
            'company_id': self.company_id.id,
        }
        return payment_vals

    # Override Order Now Methods
    @api.multi
    def action_order_config_done(self):

        self.ensure_one()

        # Check if advance payment is greater than the total amount
        if self.advance_amount > self.price_total:
            raise UserError(_("The Advance Amount exceeds the Total Amount.\nMake it equal to Total Amount !"))

        order_done = super(YgenOrderNow, self).action_order_config_done()

        if self.advance_amount:
            Payment = self.env['account.payment']
            payment = Payment.create(self._prepare_payment(self.order_id.amount_total))

            # For the purpose of advance amount for respective sale order
            payment.write({
                'adv_sale_id': self.order_id.id
            })
            self.order_id.is_adv = True

            payment.post()

            # Log advance amount if provided
            msg = ""
            msg += "<b>Advance Amount</b><br/>"
            msg += "<li>" + str(self.advance_amount) + "/-"
            self.order_id.message_post(body=msg)
        return order_done

    @api.multi
    def action_new_order_config_done(self):

        self.ensure_one()

        # Check if advance payment is greater than the total amount
        if self.advance_amount > self.price_total:
            raise UserError(_("The Advance Amount exceeds the Total Amount.\nMake it equal to Total Amount !"))

        order_done = super(YgenOrderNow, self).action_new_order_config_done()

        if self.advance_amount:
            Payment = self.env['account.payment']
            payment = Payment.create(self._prepare_payment(self.order_id.amount_total))
            
            # For the purpose of advance amount for respective sale order
            payment.write({
                'adv_sale_id': self.order_id.id
            })
            self.order_id.is_adv = True

            payment.post()

            # Log advance amount if provided
            msg = ""
            msg += "<b>Advance Amount</b><br/>"
            msg += "<li>" + str(self.advance_amount) + "/-"
            self.order_id.message_post(body=msg)
        return order_done
