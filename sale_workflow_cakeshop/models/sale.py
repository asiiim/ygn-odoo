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
        copy=False
    )
    advance_payment = fields.Monetary(related="payment_id.amount", string="Advance", store=True, track_visibility='onchange')
    amount_due = fields.Monetary(compute='_compute_amount_due', string='Amount Due', store=True, readonly=True, track_visibility='onchange')
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

    @api.depends('amount_total', 'total_return_adv', 'payment_id', 'total_adv')
    def _compute_amount_due(self):
        """
        Compute the amount due of the SO.
        """
        for line in self:
            if not line.invoice_ids:
                line.amount_due = line.amount_total + line.total_return_adv - line.total_adv

    # Validate Stock Picking Operation
    delivery_validated = fields.Boolean('Delivery Validated?', default=False, readonly=True, copy=False)

    @api.multi
    def validate_picking(self):
        for so in self:
            stock_pickings = so.mapped('picking_ids').filtered(lambda r: r.state != 'cancel')
            # stock_pickings = self.env['stock.picking'].search([('origin', '=', so.name), ('state', '!=', 'cancel')])
            if stock_pickings:
                for stock_picking in stock_pickings:
                    if stock_picking.state not in ["done", "cancel"]:
                        stock_picking.button_validate()
                    so.write({'delivery_validated': True})
            else:
                raise UserError(_('No such deliveries to validate.'))

    # Tender and Change
    tender_amount = fields.Monetary(string='Tender', track_visibility='onchange', default=0.0)
    change_amount = fields.Monetary(string='Change', track_visibility='onchange', default=0.0)

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
        #todo: this extension works if there is only one invoice to create.
        # What about user selects more thatn one orders to create invoice?
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
        self.ensure_one()
        return self.env.ref('sale_workflow_cakeshop.action_report_sale_or_kitchen_order').report_action(self)

    # View related kitchen orders of the sale order
    @api.multi
    def view_kitchen_order(self):
        self.ensure_one()
        # return list view action if there are more than one KOs, or 
        # return form view if there is only one ko else return tree view
        action = {
            'name': _('Kitchen Order'),
            'res_model': 'kitchen.order',
            'views': [(self.env.ref('kitchen_order.view_kitchen_order_tree').id, 'tree')],
            'type': 'ir.actions.act_window',
            'target':'new'
        }

        kitchen_orders = self.mapped('kitchen_order_ids')
        if len(kitchen_orders) > 1:
            action['domain'] = [('id', 'in', kitchen_orders.ids)]
        elif kitchen_orders:
            action['views'] = [(self.env.ref('kitchen_order.view_kitchen_order_form').id, 'form')]
            action['res_id'] = kitchen_orders.id
        return action

    # Change requested date
    @api.multi
    def action_change_requested_date(self):
        """Return action to change the requested date"""
        self.ensure_one()
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

    # Provide Reference Product
    ref_product_id = fields.Many2one(comodel_name='product.product', string='Reference Product', domain="[('sale_ok', '=', True), ('is_custom', '=', False), ('is_addon', '=', False)]")

    # Edit sale order
    @api.multi
    def action_edit_sale_order(self):
        self.ensure_one()

        kitchen_orders = self.mapped('kitchen_order_ids')
        ko_note = ""
        base_product = None
        qty = 0.0

        if len(kitchen_orders) == 1:
            ko_note = kitchen_orders.ko_note
            base_product = kitchen_orders.product_id
            qty = kitchen_orders.product_uom_qty
        
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
                default_ref_product_id = self.ref_product_id.id,
                default_source_id = self.source_id.id,
                default_team_id = self.team_id.id,
                default_ko_note = ko_note,
                default_prd_id = base_product.id,
                default_product_uom_qty = qty,
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

    @api.multi
    def advance_payment_option(self): 
        self.ensure_one()
        sale_change_advance_view_id = self.env.ref('sale_workflow_cakeshop.sale_change_advance_form').id
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

    # Add multiple advance payment
    is_adv = fields.Boolean("Advance Received", default=False)
    adv_payment_ids= fields.One2many('account.payment', 'adv_sale_id', string="Advance Payments")
    total_adv = fields.Monetary(compute='_compute_total_adv', string='Total Advance', store=True, readonly=True, track_visibility='onchange')

    @api.depends('is_adv', 'adv_payment_ids')
    def _compute_total_adv(self):
        """
        Compute the total advance payments of the SO.
        """
        for so in self:
            if so.is_adv:
                for adv in so.adv_payment_ids:
                    so.total_adv += adv.amount
    
    @api.multi
    def return_excess_advance_payment(self):
        self.ensure_one()
        if self.amount_due < 0:
            if self.state != 'sale':
                raise UserError(_('You must confirm the sale order first.'))
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
    
    # Cancel Kitchen Orders, Delivery and Advance if SO is Cancelled
    @api.multi
    def action_cancel(self):
        kitchen_orders = self.mapped('kitchen_order_ids')
        # Cancel Kitchen Orders
        kitchen_orders.cancel_kitchen_order()
        
        # Cancel Delivery
        # self.mapped('picking_ids').action_cancel()
        # stock_picking = self.env['stock.picking'].search([('origin', '=', self.name), ('state', '!=', 'cancel')], limit=1)
        # if stock_picking.state not in ["done", "cancel"]:
        #     stock_picking.action_cancel()
        return super(SaleOrder, self).action_cancel()

    # Change customer
    @api.multi
    def action_change_customer(self):
        """Return action to change the customer"""
        self.ensure_one()
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
    
    # Unlink delivery if so is deleted
    @api.multi
    def unlink(self):
        for order in self:
            if order.is_advance:
                raise UserError(_('You must cancel the advance payment first.'))
            stock_pickings = order.mapped('picking_ids').filtered(lambda r: r.state == 'cancel')
            stock_pickings.unlink()
            # self.env['stock.picking'].search([('origin', '=', order.name), ('state', '=', 'cancel')])
            # for pick in stock_pickings:
            #     pick.unlink()
        return super(SaleOrder, self).unlink()

    # Make sale order
    @api.multi
    def action_make_order(self):
        self.ensure_one()
        order_make_view_id = self.env.ref('sale_workflow_cakeshop.make_order_form').id
        ref_product_id = ""
        qty = 0

        # Taking first orderline detail as the reference product, qty and unit of measure
        for line in self.order_line:
            ref_product_id = line.product_id.id
            qty = line.product_uom_qty
            break

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.configurator.ordernow.ko',
            'name': "Make Sale Order",
            'view_mode': 'form',
            'view_id': order_make_view_id,
            'target': 'new',
            'context': dict(
                self.env.context,
                default_order_id=self.id,
                default_partner_id = self.partner_id.id,
                default_requested_date = self.requested_date,
                default_saleorder_date = self.date_order,
                default_ref_product_id = ref_product_id,
                default_product_uom_qty = qty,
                wizard_model = 'product.configurator.ordernow.ko'
            )
        }

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    on_hand = fields.Float(related="product_id.qty_available", string="On Hand")
