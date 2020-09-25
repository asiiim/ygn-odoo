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
    
    payment_mode = fields.Selection([('add', 'Add'), ('rmv', 'Remove')], string='Add/Remove Advance', default='add')
    amount_due = fields.Monetary(related="so_id.amount_due", string='Amount Due', store=True, readonly=True)
    total_adv = fields.Monetary(related="so_id.total_adv", string='Total Advance', store=True, readonly=True)
    is_adv_return = fields.Boolean(related="so_id.is_adv_return", string='Advanced Returned', store=True, readonly=True)

    def _domain_payment_id(self):
        sale_id = self.so_id.id
        domain = [('payment_type', '=', 'inbound'), ('state','in', ('sent','posted')), ('move_reconciled', '=', False), ('adv_sale_id', '=', sale_id)]
        return domain
    
    payment_id = fields.Many2one(comodel_name='account.payment', domain=_domain_payment_id, string="Advance Payment")
    cancel_payment_id = fields.Many2one(comodel_name='account.payment', string="Select Cancel Payment")

    add_advance = fields.Boolean(related="so_id.is_adv", string='Advance', readonly=True, default=False)


    # Selected advance payment details
    is_adv_sel = fields.Boolean("Payment Selected", compute="_payment_select", store=True)
    sel_adv_amt = fields.Monetary(related="cancel_payment_id.amount", string='Amount', readonly=1)
    sel_adv_memo = fields.Char(related="cancel_payment_id.communication", string="Memo", readonly="1")
    sel_adv_date = fields.Date(related="cancel_payment_id.payment_date", string='Payment Date', readonly="1")
    sel_pay_journ = fields.Many2one(related="cancel_payment_id.journal_id", string='Payment Journal', readonly="1")
    currency_id = fields.Many2one(related="cancel_payment_id.currency_id", readonly="1")

    @api.depends('cancel_payment_id')
    def _payment_select(self):
        for rec in self:
            if rec.cancel_payment_id:
                rec.is_adv_sel = True
            else:
                rec.is_adv_sel = False

    @api.multi
    def _prepare_payment(self, payment_mode):
        """
        Prepare the dict of values to create the new payment for a advance payment.
        """
        self.ensure_one()
        if payment_mode == 'add':
            payment_methods = self.journal_id.inbound_payment_method_ids
            payment_method_id = payment_methods and payment_methods[0] or False
            payment_vals = {
                'payment_method_id': payment_method_id.id,
                'payment_type': 'inbound',
                'amount': self.adv_amount,
                'journal_id': self.journal_id.id,
                'payment_date': self.payment_date,
                'communication': 'New Advance Payment for order no %s' % self.so_id.name,
                'company_id': self.company_id.id
        }
        else:
            payment_methods = self.cancel_payment_id.journal_id.outbound_payment_method_ids
            payment_method_id = payment_methods and payment_methods[0] or False
            payment_vals = {
            'payment_method_id': payment_method_id.id,
            'payment_type': 'outbound',
            'amount': self.cancel_payment_id.amount,
            'journal_id': self.cancel_payment_id.journal_id.id,
            'payment_date': self.cancel_payment_id.payment_date,
            'communication': 'Return Advance Payment to for order no %s' % self.so_id.name,
            'company_id': self.company_id.id
        }
        payment_vals.update({
            'partner_type': 'customer',
            'partner_id': self.so_id.partner_id.id,
        })
        return payment_vals

    @api.multi
    def add_advance_payment(self):
        # Check if advance payment is greater than the total amount
        if self.payment_mode == "add":
            if self.adv_amount and self.adv_amount > self.so_id.amount_due:
                raise UserError(_("The Advance Amount exceeds the Total Due Amount.\nOr, make it equal to Total Due Amount !"))
            elif self.adv_amount <= 0:
                raise UserError(_("Enter amount greater than zero !"))
            else:
                Payment = self.env['account.payment']
                payment_vals = self._prepare_payment(self.payment_mode)
                payment = Payment.create(payment_vals)
                payment.write({'adv_sale_id': self.so_id.id})
                payment.post()
                self.so_id.write({
                    'is_adv': True
                })
        else:
            raise UserError(_("Wrong payment mode selected !"))

    @api.multi
    def remove_advance_payment(self):
        self.ensure_one()
        if self.payment_mode == "rmv":
            if self.total_adv:
                if self.cancel_payment_id:
                    Payment = self.env['account.payment']
                    payment_vals = self._prepare_payment(self.payment_mode)
                    payment = Payment.create(payment_vals)
                    payment.write({'sale_id': self.so_id.id})
                    payment.post()
                    # Open payment matching screen
                    self.cancel_payment_id = None
                    self.so_id.write({
                        'is_adv_return': True
                    })
                    return payment.open_payment_matching_screen()
                else:
                    raise UserError(_('Select the payment you want to remove.'))
            else:
                raise UserError(_('No advance payments to remove.'))
        else:
            raise UserError(_("Wrong payment mode selected !"))

