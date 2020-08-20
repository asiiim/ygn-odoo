# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, api, _
from odoo.exceptions import Warning, ValidationError, UserError

from odoo.addons import decimal_precision as dp

import logging

_logger = logging.getLogger(__name__)


class ProductConfiguratorSaleOrderKO(models.TransientModel):
    _name = 'product.configurator.ordernow.ko'

    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        domain=[('config_ok', '=', True)],
        string='Configurable Template'
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        domain="[('sale_ok', '=', True), ('is_custom', '=', True)]",
        required=True
    )
    product_uom_id = fields.Many2one(related='product_id.uom_id', readonly=True)
    uom = fields.Char(related='product_uom_id.name', string='UOM')
    
    order_id = fields.Many2one(
        comodel_name='sale.order',
        # required=True,
        readonly=True
    )
    payment_id = fields.Many2one(
        comodel_name='account.payment',
        # required=True,
        readonly=True
    )
    
    saleorder_date = fields.Datetime(string='Order Date', required=True, index=True, copy=False, default=fields.Datetime.now)

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        # required=True,
        readonly=False,
        string="Customer"
    )

    requested_date = fields.Datetime(string='Requested Date', required=True, index=True, copy=False)
    name_for_message = fields.Char(string="Name for Message", copy=False)
    ko_note = fields.Text(string="KO Note", track_visibility='onchange')
    client_order_ref = fields.Char(string='Customer Reference', copy=False)
    amount = fields.Monetary(string='Advance Amount', required=True, default=0)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    journal_id = fields.Many2one('account.journal', string='Payment Journal', domain=[('type', 'in', ('bank', 'cash'))], default=lambda self: self.env['account.journal'].search([('type', '=', 'cash')], limit=1))
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
    price_unit = fields.Float(string="Price", digits=dp.get_precision('Unit Price'), oldname="price", compute="_compute_price")
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    
    # discount styles
    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'), default=0.0)
    fix_discount = fields.Float(string='Fixed Discount', default=0.0)
    
    tax_id = fields.Many2many('account.tax', related="product_id.taxes_id",string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True)

    ko_notes_ids = fields.Many2many('kitchen.order.notes', 'sale_workflow_cakeshop_kitchen_order_notes_', string='KO Notes')
    order_message_id = fields.Many2one('kitchen.message', string='Message')
    
    # Add manual price during order
    manual_price = fields.Float(string="Manual Price", digits=dp.get_precision('Manual Price'))

    # Product Addons Line
    product_addon_lines = fields.One2many('product.addons.line', 'product_config_soko', string="Addon Lines")

    # Sales Channel In Wizard
    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()
    
    team_id = fields.Many2one('crm.team', 'Sales Channel', change_default=True, default=_get_default_team, oldname='section_id')

    # Compute unit price
    @api.depends('product_id', 'product_addon_lines')
    def _compute_price(self):
        self.price_unit = self.product_id.list_price
    
    # Compute total price
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'manual_price', 'product_addon_lines', 'fix_discount')
    def _compute_amount(self):

        for line in self:
            addon_price = 0.0

            # check if it has unit price or manual price
            if line.manual_price:
                price = line.manual_price
            else:
                price = line.price_unit

            # check if product addons are selected
            if line.product_addon_lines:
                for addon in line.product_addon_lines:
                    addon_price += addon.amount

                price *= line.product_uom_qty
                price += addon_price
                price /= line.product_uom_qty
            
            # apply discount if provided
            if line.discount:
                price *= (1 - (line.discount or 0.0) / 100.0)
            elif line.fix_discount:
                price -= (line.fix_discount / line.product_uom_qty)

            taxes = line.tax_id.compute_all(price, line.currency_id, line.product_uom_qty, product=line.product_id, partner=line.partner_id)
            
            line.update({
                'price_total': taxes['total_included']
            })

    @api.multi
    def _prepare_kitchen_order(self):
        """
        Prepare the dict of values to create the new kitchen order for a new order. This method may 
        be overridden to implement custom invoice generation (making sure to call super() to 
        establish a clean extension chain).
        """
        self.ensure_one()
        notes = ''
        for note in self.ko_notes_ids:
            notes += note.name + "\n"
        if self.ko_note:
            notes += self.ko_note
        if self.product_addon_lines:
            notes += "\nAddons:\n"
            for addon in self.product_addon_lines:
                notes += "- "
                notes += addon.addon_id.name
                notes += " x" + str(int(addon.quantity))
                notes += "\n"

        ko_vals = {
            'product_id': self.product_id.id,
            'requested_date': self.requested_date,
            'ref_product_id': self.ref_product_id.id,
            'saleorder_id': self.order_id.id,
            'name_for_message': self.name_for_message or '',
            'ko_note': notes,
            'ko_notes_ids': self.ko_notes_ids,
            'product_uom_qty': self.product_uom_qty,
            'company_id': self.company_id.id,
            'message_id': self.order_message_id.id
        }
        return ko_vals

    # select print option for KO & SO
    kitchen_sale_order_print_selection = fields.Selection([('ko', 'Kitchen Order'), ('so', 'Sale Order'), ('both', 'Both')], string="Print SO/KO", default="both")

    @api.multi
    def _prepare_order(self):
        """
        Prepare the dict of values to create the new order for a new order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        order_vals = {
            'partner_id': self.partner_id.id,
            'date_order': self.saleorder_date,
            'requested_date': self.requested_date,
            'team_id': self.team_id.id,
            'company_id': self.company_id.id,
            'kitchen_sale_order_print_selection': self.kitchen_sale_order_print_selection
        }
        return order_vals

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
        if self.price_total == self.amount:
            adv_amt = so_amount
        else:
            adv_amt = self.amount

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

    def _get_order_line_vals(self, product_id):
        """Hook to allow custom line values to be put on the newly
        created or edited lines."""
        product = self.env['product.product'].browse(product_id)
        
        # Add addon description and price unit in orderline
        orderline_desc = product.name or ""
        addon_price = 0.0
        discount = 0.0
        fix_discount = 0.0
        addon_details = ""

        if self.product_addon_lines:
            for addon in self.product_addon_lines:
                orderline_desc += " | "
                orderline_desc += addon.addon_id.name
                
                addon_price += addon.amount
                
                addon_details += "<li>" + str(addon.addon_id.name) + " x" + str(addon.quantity) + " @" + str(addon.unit_price) + " = " + str(addon.amount) + "/-<br/>"
                    
            self.price_unit *= self.product_uom_qty
            self.price_unit += addon_price
            self.price_unit /= self.product_uom_qty
        

        # apply discount if provided
        if self.discount:
            discount = self.discount
        elif self.fix_discount:
            fix_discount = self.fix_discount / self.product_uom_qty
        
        return {
            'product_id': product_id,
            'name': orderline_desc,
            'price_unit': self.manual_price if self.manual_price else self.price_unit,
            'product_uom_qty': self.product_uom_qty,
            'product_uom': product.uom_id.id,
            'discount': discount,
            'discount_fixed': fix_discount,
            'uom_name': product.uom_id.name,
            'addon_details': addon_details
        }

    @api.multi
    def action_order_config_done(self):
        """Parse values and execute final code before closing the wizard"""

        # Check if advance payment is greater than the total amount
        if self.amount > self.price_total:
            raise UserError(_("The Advance Amount exceeds the Total Amount.\nMake it equal to Total Amount !"))

        # Check if product template exists
        if not self.product_tmpl_id:
            self.product_tmpl_id = self.product_id.product_tmpl_id

        # Check if manual price is less than the computed unit price
        if self.manual_price and self.manual_price < self.price_unit:
            raise UserError(_('Manual price cannot be set less than the Standard Price.\n Please check Manual Price again !'))

        # Check sale order from the context
        if not self.order_id:
            SaleOrder = self.env['sale.order']
            sale_order = SaleOrder.create(self._prepare_order())
            
            self.order_id = sale_order

            # Attach sale order line
            line_vals = self._get_order_line_vals(self.product_id.id)
            self.order_id.write({'order_line': [(0, 0, line_vals)]})

            # Create Kitchen Order
            KitchenOrder = self.env['kitchen.order']
            KitchenOrder.create(self._prepare_kitchen_order())
            
            # Create Payment if any
            if self.amount:
                Payment = self.env['account.payment']
                payment = Payment.create(self._prepare_payment(sale_order.amount_total))
                
                # For the purpose of advance amount for respective sale order
                payment.write({
                    'adv_sale_id': sale_order.id
                })
                sale_order.is_adv = True

                payment.post()
                # self.payment_id = payment
                # sale_order.payment_id = payment
            
            # Confirm the sale order
            sale_order.action_confirm()

            # sale order form view reference
            sale_order_form_ref_id = self.env.ref('sale.view_order_form').id

            # Log the sale order details in the chatter
            orderline_vals = self._get_order_line_vals(self.product_id.id)
            msg = "<b>Order Details</b><br/>"
            msg += "<li>Product: " + str(orderline_vals.get('name')) + "<br/>"
            msg += "<li>Qty: " + str(orderline_vals.get('product_uom_qty')) + " " + str(orderline_vals.get('uom_name')) + "<br/>"
            
            if self.product_addon_lines:
                msg += "<br/><b>Addons Details</b><br/>"
                msg += str(orderline_vals.get('addon_details'))

            if self.discount:
                msg += "<br/><b>Discount</b><br/>"
                msg += "<li>" + str(self.discount) + "%"
            elif self.fix_discount:
                msg += "<br/><b>Fix Discount</b><br/>"
                msg += "<li>" + str(self.fix_discount) + "/-"
            
            self.order_id.message_post(body=msg)
            
            # Set reference product in sale order if provided
            if self.ref_product_id:
                self.order_id.write({'ref_product_id': self.ref_product_id.id})

            # Show sale order form view
            return {
                'name': _('Sale Order'),
                'res_model': 'sale.order',
                'res_id': self.order_id.id,
                'views': [(sale_order_form_ref_id, 'form')],
                'type': 'ir.actions.act_window'
            }
        else:
            # Check if the sale order is not a quotation
            if self.order_id.state not in ["draft", "sent"]:
                
                # Cancel the existing stock delivery
                stock_picking = self.env['stock.picking']
                stock_picking.search([('origin', '=', self.order_id.name)], limit=1).action_cancel()

                # Cancel the sale order
                self.order_id.action_cancel()

                # Set the sale order to quotation
                self.order_id.action_draft()

            # Place new vals for the sale order
            self.order_id.write(self._prepare_order())

            # Replace sale order line with new product
            line_vals = self._get_order_line_vals(self.product_id.id)
            for orderline in self.order_id.order_line:
                if self.ref_product_id.is_custom:
                    raise UserError(_("The product you are trying to reference might be a custom product !\n Try selecting available reference product."))
                else:
                    self.order_id.write({'order_line': [(1, orderline.id, line_vals)]})
                    break

            # Changes in KO
            ko_vals = self._prepare_kitchen_order()
            if self.order_id.kitchen_order_ids:
                for ko in self.order_id.kitchen_order_ids:
                    ko.start_kitchen_order()
                    ko.write({
                        'product_uom_qty': ko_vals.get('product_uom_qty'),
                        'ko_note': ko_vals.get('ko_note'),
                        'ref_product_id': self.ref_product_id.id
                    })
                    break 
            else:
                # Create Kitchen Order
                KitchenOrder = self.env['kitchen.order']
                KitchenOrder.create(self._prepare_kitchen_order())
            
            # Create Payment if the order is in draft and has entered advance
            if self.amount:
                Payment = self.env['account.payment']
                payment = Payment.create(self._prepare_payment(self.order_id.amount_total))
                # For the purpose of advance amount for respective sale order
                payment.write({
                    'adv_sale_id': sale_order.id
                })
                sale_order.is_adv = True
                payment.post()
                # self.payment_id = payment
                # self.order_id.payment_id = payment

            # Confirm the sale order
            self.order_id.action_confirm()

            # Log the sale order details in the chatter
            orderline_vals = self._get_order_line_vals(self.product_id.id)
            msg = "<b>Order Details</b><br/>"
            msg += "<li>Product: " + str(orderline_vals.get('name')) + "<br/>"
            msg += "<li>Qty: " + str(orderline_vals.get('product_uom_qty')) + " " + str(orderline_vals.get('uom_name')) + "<br/>"
            msg += "<br/><b>Addons Details</b><br/>"
            
            if self.product_addon_lines:
                msg += "<br/><b>Addons Details</b><br/>"
                msg += str(orderline_vals.get('addon_details'))

            if self.discount:
                msg += "<br/><b>Discount</b><br/>"
                msg += "<li>" + str(self.discount) + "%"
            elif self.fix_discount:
                msg += "<br/><b>Fix Discount</b><br/>"
                msg += "<li>" + str(self.fix_discount) + "/-"
            
            self.order_id.message_post(body=msg)
        
            # Set reference product in sale order if provided
            if self.ref_product_id:
                self.order_id.write({'ref_product_id': self.ref_product_id.id})

    # To Trigger order details wizard view 
    @api.multi
    def view_order_description(self):
        ko_id = []
        
        for ko in self.order_id.kitchen_order_ids:
            ko_id.append(ko.id)
        
        return {
            'name': _('Kitchen Order'),
            'res_model': 'kitchen.order',
            'res_id': ko_id[0],
            'views': [(self.env.ref('sale_workflow_cakeshop.kitchen_order_form_inherit').id, 'form')],
            'type': 'ir.actions.act_window',
            'target':'new'
        }
    
    @api.multi
    def action_new_order_config_done(self):
        """Parse values and execute final code before closing the wizard"""

        # Check if advance payment is greater than the total amount
        if self.amount > self.price_total:
            raise UserError(_("The Advance Amount exceeds the Total Amount.\nMake it equal to Total Amount !"))

        # Check if product template exists
        if not self.product_tmpl_id:
            self.product_tmpl_id = self.product_id.product_tmpl_id

        # Check if manual price is less than the computed unit price
        if self.manual_price and self.manual_price < self.price_unit:
            raise UserError(_('Manual price cannot be set less than the Standard Price.\n Please check Manual Price again !'))

        SaleOrder = self.env['sale.order']
        sale_order = SaleOrder.create(self._prepare_order())
        
        self.order_id = sale_order

        # Attach sale order line
        line_vals = self._get_order_line_vals(self.product_id.id)
        self.order_id.write({'order_line': [(0, 0, line_vals)]})
        
        # Set reference product in sale order if provided
        if self.ref_product_id:
            self.order_id.write({'ref_product_id': self.ref_product_id.id})
        
        # Create Kitchen Order
        KitchenOrder = self.env['kitchen.order']
        KitchenOrder.create(self._prepare_kitchen_order())
        
        # Create Payment if any
        if self.amount:
            Payment = self.env['account.payment']
            payment = Payment.create(self._prepare_payment(sale_order.amount_total))
            # For the purpose of advance amount for respective sale order
            payment.write({
                'adv_sale_id': sale_order.id
            })
            sale_order.is_adv = True
            payment.post()
            # self.payment_id = payment
            # sale_order.payment_id = payment

        #Confirm Sale Order
        sale_order.action_confirm()

        # Log the sale order details in the chatter
        orderline_vals = self._get_order_line_vals(self.product_id.id)
        msg = "<b>Order Details</b><br/>"
        msg += "<li>Product: " + str(orderline_vals.get('name')) + "<br/>"
        msg += "<li>Qty: " + str(orderline_vals.get('product_uom_qty')) + " " + str(orderline_vals.get('uom_name')) + "<br/>"
        msg += "<br/><b>Addons Details</b><br/>"
        
        if self.product_addon_lines:
            msg += "<br/><b>Addons Details</b><br/>"
            msg += str(orderline_vals.get('addon_details'))

        if self.discount:
            msg += "<br/><b>Discount</b><br/>"
            msg += "<li>" + str(self.discount) + "%"
        elif self.fix_discount:
            msg += "<br/><b>Fix Discount</b><br/>"
            msg += "<li>" + str(self.fix_discount) + "/-"
        
        self.order_id.message_post(body=msg)

        # Ask to print the order/kitchen order
        return self.view_order_description()

    # Provide Reference Product
    ref_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Reference Product',
        domain="[('sale_ok', '=', True), ('is_custom', '=', False), ('is_addon', '=', False)]"
    )

class ProductAddonsLine(models.TransientModel):
    _name = "product.addons.line"
    _description = 'Product Addon Line'
    _order = 'addon_id, sequence, id'
    
    sequence = fields.Integer(string='Sequence', default=10)
    product_config_soko = fields.Many2one('product.configurator.ordernow.ko', string="Product Config SOKO")
    addon_id = fields.Many2one('product.product', string="Addon", domain="[('is_addon', '=', True), ('sale_ok', '=', True)]", ondelete='restrict', required=True, oldname="product_id")
    quantity = fields.Float(string='Qty', default=1.0)
    uom_id = fields.Many2one(related="addon_id.uom_id", string="UOM")
    unit_price = fields.Float(string='Rate', required=True)
    amount = fields.Float(string='Amount', compute="_compute_addon_amount")

    @api.depends('quantity', 'unit_price')
    def _compute_addon_amount(self):
        for addon in self:
            if addon.quantity and addon.unit_price:
                addon.amount = addon.quantity * addon.unit_price
            else:
                addon.amount = 0.0

    @api.multi
    @api.onchange('addon_id')
    def get_product_unit_price(self):

        vals = {}
        vals['unit_price'] = self.addon_id.list_price
        self.update(vals)

class ProductOrderDescription(models.TransientModel):
    _name = "product.order.desc"
    _description = 'Product Order Description'
    

    so_id = fields.Many2one('sale.order', string='Order Ref.')
    ko_ids = fields.One2many(related='so_id.kitchen_order_ids', string="Kitchen Order Ref.")

    # Print SO or KO
    @api.multi
    def print_order(self):
        return self.so_id.print_koso_report()

    # Order again
    @api.multi
    def new_order(self):
        new_order_configurator_view_id = self.env.ref('sale_workflow_cakeshop.product_configurator_ordernow_ko_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.configurator.ordernow.ko',
            'name': "New Order Configurator",
            'view_mode': 'form',
            'view_id': new_order_configurator_view_id,
            'target': 'new',
            'context': dict(
                self.env.context,
                default_product_tmpl_id=None,
                default_product_id=None,
                wizard_model='product.configurator.ordernow.ko',
            )
        }
    
    # Order again
    @api.multi
    def view_order(self):
        sale_order_form_ref_id = self.env.ref('sale.view_order_form').id
        return {
            'name': _('Sale Order'),
            'res_model': 'sale.order',
            'res_id': self.so_id.id,
            'views': [(sale_order_form_ref_id, 'form')],
            'type': 'ir.actions.act_window'
        }
    