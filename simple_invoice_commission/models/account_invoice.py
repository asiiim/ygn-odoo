# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import _, api, exceptions, fields, models

class CommissionInvoiceLine(models.Model):
    _inherit ="account.invoice.line"

    commission_subtotal = fields.Float(string='Commission Subtotal', compute="_compute_commission_total", readonly=True, store=True,track_visibility='always')

    @api.depends('account_analytic_id','price_subtotal')
    def _compute_commission_total(self):
        for record in self:
            if record.account_analytic_id:
                record.commission_subtotal = record.account_analytic_id.partner_id.commission * 0.01 * float(record.price_subtotal)
            else:
                record.commission_subtotal = 0.0

class CommisionAccountAnalyticLine(models.Model):
    _inherit ="account.analytic.line"

    commission_subtotal = fields.Float(string='Commission Subtotal',compute="_compute_analytic_commission_total",store=True,track_visibility='always')

    @api.depends('account_id','amount')
    def _compute_analytic_commission_total(self):
        for record in self:
            if record.account_id:
                record.commission_subtotal = record.account_id.partner_id.commission * 0.01 * float(record.amount)
            else:
                record.commission_subtotal = 0.0