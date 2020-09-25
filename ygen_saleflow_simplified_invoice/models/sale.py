# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import Warning, ValidationError, UserError

import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Tender and Change
    tender_amount = fields.Monetary(string='Tender', default=0.0, track_visibility='onchange')
    change_amount = fields.Monetary(string='Change', default=0.0, track_visibility='onchange')

    # Return Invoice Line Vals
    def _get_line_vals(self, saleorder, invoice, account_id, tax_ids):
        invlines = [(5, 0, 0)]
        for line in saleorder.order_line:
            data = {
                'name': line.name,
                'origin': saleorder.name,
                'invoice_id': invoice.id,
                'account_id': account_id.id,
                'price_unit': line.price_unit,
                'quantity': line.product_uom_qty,
                'discount': line.discount,
                'discount_fixed': line.discount_fixed,
                'uom_id': line.product_id.uom_id.id,
                'product_id': line.product_id.id,
                'sale_line_ids': [(6, 0, [line.id])],
                'invoice_line_tax_ids': [(6, 0, tax_ids.ids)],
                'account_analytic_id': saleorder.analytic_account_id.id or False,
            }
            invlines.append((0, 0, data))
        return invlines

    # Multi Invoice Payment
    @api.multi
    def pay_bill(self):
        for so in self:
            if so.invoice_status == 'to invoice':
                so.write({
                    'tender_amount': so.amount_due,
                    'change_amount': 0
                })
                
                # Invoice Object
                inv_obj = self.env['account.invoice']
                
                # Get Account and Taxes
                account_id = False
                tax = False
                tax_ids = False

                for line in so:
                    account_id = so.fiscal_position_id.map_account(line.product_id.property_account_income_id or line.product_id.categ_id.property_account_income_categ_id)
                    tax = line.product_id.taxes_id.filtered(lambda r: not so.company_id or r.company_id == so.company_id)
                    break
                if not account_id:
                    raise UserError(_('There is no income account defined for the product in orderline.'))
                
                # Tax
                if so.fiscal_position_id and tax:
                    tax_ids = so.fiscal_position_id.map_tax(tax)
                else:
                    tax_ids = tax
                
                # Create Invoice
                invoice = inv_obj.create({
                    'name': so.name,
                    'origin': so.name,
                    'type': 'out_invoice',
                    'reference': False,
                    'account_id': so.partner_id.property_account_receivable_id.id,
                    'partner_id': so.partner_invoice_id.id,
                    'partner_shipping_id': so.partner_shipping_id.id,
                    'currency_id': so.pricelist_id.currency_id.id,
                    'payment_term_id': so.payment_term_id.id,
                    'fiscal_position_id': so.fiscal_position_id.id or so.partner_id.property_account_position_id.id,
                    'team_id': so.team_id.id,
                    'user_id': so.user_id.id,
                    'comment': so.note,
                })

                vals = so._get_line_vals(so, invoice, account_id, tax_ids)
                invoice.write({'invoice_line_ids': vals})     

                invoice.compute_taxes()
                invoice.message_post_with_view('mail.message_origin_link',
                            values={'self': invoice, 'origin': so},
                            subtype_id=self.env.ref('mail.mt_note').id)

                invoice = so.invoice_ids.filtered(lambda inv: inv.amount_total_signed > 0 and inv.state == 'draft')[0]
                
                if invoice and not invoice.action_invoice_open():
                    raise UserError(_("Invoice could not be validated, you can review them before validation."))
                
                # Reconcile advance payment
                if so.is_adv:
                    for adv in so.adv_payment_ids:
                        if not adv.move_reconciled:
                            credit_aml = adv.move_line_ids.filtered(lambda aml: aml.credit > 0)
                            invoice.assign_outstanding_credit(credit_aml.id)

                # Register the payment
                journal_id = self.env['account.journal'].search([('type', '=', 'cash')], limit=1)
                if so.amount_due > 0.0:
                    payment_methods = journal_id.inbound_payment_method_ids
                    payment_method_id = payment_methods and payment_methods[0] or False

                    payment_vals = {
                        'payment_method_id': payment_method_id.id,
                        'payment_type': 'inbound',
                        'partner_type': 'customer',
                        'partner_id': so.partner_id.id,
                        'amount': so.amount_due,
                        'journal_id': journal_id.id,
                        'payment_date': fields.Date.today(),
                        'communication': 'Total Due Payment for order no %s' % so.name,
                        'company_id': so.company_id.id,
                        'invoice_ids': [(4, invoice.id)],
                        'adv_sale_id': so.id
                    }

                    payment_obj = self.env['account.payment']
                    payment = payment_obj.create(payment_vals)
                    payment.post()
                    so.payment_id = payment

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        invoice_ids_arr = super(SaleOrder, self).action_invoice_create(grouped, final)
        invoice_ids = self.env['account.invoice'].browse(invoice_ids_arr)
        for inv in invoice_ids:
            inv.write({
                'tender_amount': self.tender_amount,
                'change_amount': self.change_amount
            })
        return invoice_ids_arr
