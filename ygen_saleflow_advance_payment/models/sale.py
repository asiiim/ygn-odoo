# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import Warning, ValidationError, UserError

import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_id = fields.Many2one(
        comodel_name='account.payment',
        # required=True,
        readonly=True,
        copy=False,
        track_visibility='onchange'
    )
    advance_payment = fields.Monetary(related="payment_id.amount", string="Advance", store=True, track_visibility='onchange')
    amount_due = fields.Monetary(compute='_compute_amount_due', string='Amount Due', store=True, readonly=True, track_visibility='onchange')

    @api.depends('amount_total', 'total_return_adv', 'payment_id', 'total_adv')
    def _compute_amount_due(self):
        """
        Compute the amount due of the SO.
        """
        for line in self:
            if not line.invoice_ids:
                line.amount_due = line.amount_total + line.total_return_adv - line.total_adv

    # Add, Edit or Cancel the advance payment
    is_advance = fields.Boolean('Advance', compute='_compute_if_advance')

    @api.depends('payment_id')
    def _compute_if_advance(self):
        for so in self:
            if so.payment_id:
                self.is_advance = True
            else:
                self.is_advance = False
    
    @api.multi
    def _prepare_return_payment(self, amount, communication):
        """
        Prepare the dict of values to create the return payment for a paid advance.
        """
        self.ensure_one()
        payment_methods = self.payment_id.journal_id.outbound_payment_method_ids
        payment_method_id = payment_methods and payment_methods[0] or False
        payment_return_vals = {
            'payment_method_id': payment_method_id.id,
            'payment_type': 'outbound',
            'partner_type': 'customer',
            'partner_id': self.partner_id.id,
            'amount': amount,
            'journal_id': self.payment_id.journal_id.id,
            'payment_date': self.payment_id.payment_date,
            'communication': communication,
            'company_id': self.company_id.id,
            'sale_id': self.id
        }
        return payment_return_vals

    def advance_payment_option(self):
        self.ensure_one() 
        sale_change_advance_view_id = self.env.ref('ygen_saleflow_advance_payment.sale_change_advance_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.change.advance',
            'name': "Advance Payment View",
            'view_mode': 'form',
            'view_id': sale_change_advance_view_id,
            'target': 'new',
            'context': dict(
                self.env.context,
                default_so_id=self.id,
                wizard_model='sale.change.advance'
            )
        }

    # Add multiple advance payment
    is_adv = fields.Boolean("Advance Received", default=False)
    adv_payment_ids= fields.One2many('account.payment', 'adv_sale_id', string="Advance Payments")
    total_adv = fields.Monetary(compute='_compute_total_adv', string='Total Payment', store=True, readonly=True, track_visibility='onchange')

    @api.depends('is_adv', 'adv_payment_ids')
    def _compute_total_adv(self):
        """
        Compute the total advance payments of the SO.
        """
        for so in self:
            if so.is_adv:
                for adv in so.adv_payment_ids:
                    so.total_adv += adv.amount


    # Return the advance payment if amount due is less than zero
    is_adv_return = fields.Boolean("Excess Advance Return?", default=False)
    return_adv_payment_ids = fields.One2many('account.payment', 'sale_id', string="Return Payments")
    total_return_adv = fields.Monetary(compute='_compute_total_return_adv', string='Advance Returned', store=True, readonly=True, track_visibility='onchange')

    @api.depends('is_adv_return', 'return_adv_payment_ids')
    def _compute_total_return_adv(self):
        """
        Compute the total returned advance payments of the SO.
        """
        for so in self:
            if so.is_adv_return:
                for ret_adv in so.return_adv_payment_ids:
                    so.total_return_adv += ret_adv.amount

    
    @api.multi
    def return_excess_advance_payment(self):
        if self.amount_due < 0:
            if self.state != 'sale':
                raise UserError(_('You must confirm the sale first.'))
            else:
                Payment = self.env['account.payment']
                communication = 'Return Excess Advance Payment to for order no %s' % self.name
                amount = abs(self.amount_due)
                payment = Payment.create(self._prepare_return_payment(amount, communication))
                payment.post()
                self.write({
                    'is_adv_return': True
                })
                # Open payment matching screen
                return payment.open_payment_matching_screen()
    
    # Unlink delivery if so is deleted
    @api.multi
    def unlink(self):
        for order in self:
            if order.is_advance:
                raise UserError(_('You must cancel the advance payment first.'))
            stock_pickings = self.env['stock.picking'].search([('origin', '=', order.name), ('state', '=', 'cancel')])
            for pick in stock_pickings:
                pick.unlink()
        return super(SaleOrder, self).unlink()
