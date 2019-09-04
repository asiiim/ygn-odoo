# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import _, api, exceptions, fields, models

class LabCommisionAccountInvoiceLine(models.Model):
    _inherit ="account.invoice.line"

    commission_subtotal = fields.Float(string='Commission Subtotal',compute="_compute_lab_commission_total",readonly=True,store=True,track_visibility='always')

    @api.depends('account_analytic_id','price_subtotal')
    def _compute_lab_commission_total(self):
        for record in self:
            if record.account_analytic_id:
                record.commission_subtotal = record.price_subtotal-(((record.account_analytic_id.partner_id.commission) * 0.01 ) * float(record.price_subtotal))
            else:
                record.commission_subtotal = 0.0

class LabCommisionAccountAnalyticLine(models.Model):
    _inherit ="account.analytic.line"

    commission_subtotal = fields.Float(string='Commission Subtotal',compute="_compute_lab_analytic_commission_total",store=True,track_visibility='always')

    @api.depends('account_id','amount')
    def _compute_lab_analytic_commission_total(self):
        for record in self:
            if record.account_id:
                record.commission_subtotal = record.amount-(((record.account_id.partner_id.commission) * 0.01 ) * float(record.amount))
            else:
                record.commission_subtotal = 0.0