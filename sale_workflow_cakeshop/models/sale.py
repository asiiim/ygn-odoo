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
        readonly=True
    )
    advance_payment = fields.Monetary(related="payment_id.amount", string="Advance", store=True, track_visibility='always')
    amount_due = fields.Monetary(compute='_compute_amount_due', string='Amount Due', readonly=True, track_visibility='always')
    kitchen_order_ids = fields.One2many(
        comodel_name='kitchen.order',
        inverse_name='saleorder_id',
        string="Kitchen Orders",
        track_visibility='onchange'
    )
    
    # Check if SO has KO
    has_ko = fields.Boolean(compute="_has_kitchen_orders", string="Has Kitchen Order(s)")
    @api.depends('kitchen_order_ids')
    def _has_kitchen_orders(self):
        for order in self:
            if len(order.kitchen_order_ids) > 0:
                order.has_ko = True
            else:
                order.has_ko = False

    @api.depends('amount_total')
    def _compute_amount_due(self):
        """
        Compute the amount due of the SO.
        """
        for line in self:
            if not line.invoice_ids:
                # Check if the payment linked has already been matched 
                # and set the amount_due accordingly
                line.amount_due = line.amount_total - (line.payment_id.amount if line.payment_id.state == 'posted' and not line.payment_id.move_reconciled else 0)
            else:
                for invoice in line.invoice_ids:
                    line.amount_due = invoice.residual
                    break

    # Validate Stock Picking Operation
    delivery_validated = fields.Boolean('Delivery Validated?', default=False, readonly=True, copy=False)

    @api.multi
    def validate_picking(self):
        for so in self:
            stock_picking = self.env['stock.picking'].search([('origin', '=', so.name), ('state', '!=', 'cancel')], limit=1)
            if stock_picking.state not in ["done", "cancel"]:
                stock_picking.button_validate()
            so.write({'delivery_validated': True})

    # Tender and Change
    tender_amount = fields.Monetary(string='Tender', track_visibility='always', default=0.0)
    change_amount = fields.Monetary(string='Change', track_visibility='always', default=0.0)

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

            # Check amount
            if so.amount_due <= 0.00:
                raise UserError(_('The value of the payment amount must be positive.'))
            
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
            if so.payment_id:
                credit_aml = so.payment_id.move_line_ids.filtered(lambda aml: aml.credit > 0)
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
                    'invoice_ids': [(4, invoice.id)]
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

    # Print option selection for KO & SO
    kitchen_sale_order_print_selection = fields.Selection([('ko', 'Kitchen Order'), ('so', 'Sale Order'), ('both', 'Both')], string="Print Sale Order or Kitchen Order?", default="both")

    # Print SO or KO
    @api.multi
    def print_koso_report(self):
        return self.env.ref('sale_workflow_cakeshop.action_report_sale_or_kitchen_order').report_action(self)

    # View related kitchen orders of the sale order
    @api.multi
    def view_kitchen_order(self):
        ko_id = []
        
        for ko in self.kitchen_order_ids:
            ko_id.append(ko.id)
        
        return {
            'name': _('Kitchen Order'),
            'res_model': 'kitchen.order',
            'res_id': ko_id[0],
            'views': [(self.env.ref('kitchen_order.view_kitchen_order_form').id, 'form')],
            'type': 'ir.actions.act_window',
            'target':'new'
        }

    # Change requested date
    @api.multi
    def action_change_requested_date(self):
        """Return action to change the requested date"""
        sale_requested_date_view_id = self.env.ref('sale_workflow_cakeshop.sale_change_requested_date_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.requested.date',
            'name': "Change Delivery Date",
            'view_mode': 'form',
            'view_id': sale_requested_date_view_id,
            'target': 'new',
            'context': dict(
                self.env.context,
                wizard_model='sale.requested.date'
            ),
        }

    # Edit sale order
    @api.multi
    def action_edit_sale_order(self):
        order_configurator_view_id = self.env.ref('sale_workflow_cakeshop.product_configurator_ordernow_ko_product_edit_form').id

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.configurator.ordernow.ko',
            'name': "Edit Sale Order",
            'view_mode': 'form',
            'view_id': order_configurator_view_id,
            'target': 'new',
            'context': dict(
                self.env.context,
                default_order_id=self.id,
                default_partner_id = self.partner_id.id,
                default_requested_date = self.requested_date,
                default_saleorder_date = self.date_order,
                wizard_model='product.configurator.ordernow.ko',
            ),
        }

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
    def _prepare_return_payment(self):
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
            'amount': self.payment_id.amount,
            'journal_id': self.payment_id.journal_id.id,
            'payment_date': self.payment_id.payment_date,
            'communication': 'Return Advance Payment to for order no %s' % self.name,
            'company_id': self.company_id.id
        }
        return payment_return_vals

    @api.multi
    def cancel_advance_payment(self):
        # Create return Payment if any
        if self.payment_id:
            Payment = self.env['account.payment']
            payment = Payment.create(self._prepare_return_payment())
            payment.post()
            # Open payment matching screen
            self.payment_id = None
            return payment.open_payment_matching_screen()
                

    @api.multi
    def edit_advance_payment(self):
        
        sale_change_advance_view_id = self.env.ref('sale_workflow_cakeshop.sale_change_advance_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.change.advance',
            'name': "Change Advance Amount",
            'view_mode': 'form',
            'view_id': sale_change_advance_view_id,
            'target': 'new',
            'context': dict(
                self.env.context,
                default_so_id=self.id,
                wizard_model='sale.change.advance'
            )
        }

    @api.multi
    def add_advance_payment(self): 
        sale_change_advance_view_id = self.env.ref('sale_workflow_cakeshop.sale_change_advance_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.change.advance',
            'name': "Add Advance Amount",
            'view_mode': 'form',
            'view_id': sale_change_advance_view_id,
            'target': 'new',
            'context': dict(
                self.env.context,
                default_so_id=self.id,
                default_add_advance = True,
                wizard_model='sale.change.advance'
            )
        }
    
    # Cancel Kitchen Orders, Delivery and Advance if SO is Cancelled
    @api.multi
    def action_cancel(self):
        # Cancel Kitchen Orders
        for ko in self.kitchen_order_ids:
            ko.cancel_kitchen_order()
        
        # Cancel Delivery
        stock_picking = self.env['stock.picking'].search([('origin', '=', self.name), ('state', '!=', 'cancel')], limit=1)
        if stock_picking.state not in ["done", "cancel"]:
            stock_picking.action_cancel()
        self.write({'delivery_validated': False})
        return super(SaleOrder, self).action_cancel()

    # Change customer
    @api.multi
    def action_change_customer(self):
        """Return action to change the customer"""
        sale_customer_view_id = self.env.ref('sale_workflow_cakeshop.sale_change_partner_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.change.customer',
            'name': "Change Customer",
            'view_mode': 'form',
            'view_id': sale_customer_view_id,
            'target': 'new',
            'context': dict(
                self.env.context,
                wizard_model='sale.change.customer'
            ),
        }

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    on_hand = fields.Float(related="product_id.qty_available", string="On Hand")
