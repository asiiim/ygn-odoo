# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import _, api, exceptions, fields, models

class CommissionInvoiceLine(models.Model):
    _inherit ="account.invoice.line"

    commission_subtotal = fields.Float(string='Commission Subtotal', compute="_compute_commission_total", readonly=True, store=True,track_visibility='always')

    @api.depends('account_analytic_id','price_subtotal')
    def _compute_commission_total(self):
        commission_mode = self.env['ir.config_parameter'].sudo().get_param('commission_mode')
        for record in self:
            commission_rate = record.account_analytic_id.partner_id.commission
            if commission_rate:
                if commission_mode == 'discount_deducted':
                    if commission_rate > record.discount:
                        deducted_commission_rate = commission_rate - record.discount
                        record.commission_subtotal = deducted_commission_rate * 0.01 * float(record.price_subtotal)
                    else:
                        record.commission_total = 0.0
                else:
                    record.commission_subtotal = commission_rate * 0.01 * float(record.price_subtotal)
            else:
                record.commission_subtotal = 0.0
