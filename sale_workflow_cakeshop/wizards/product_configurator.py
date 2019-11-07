# -*- coding: utf-8 -*-

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
        string='Configurable Template',
        required=True
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True
    )
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
    # order_line_id = fields.Many2one(
    #     comodel_name='sale.order.line',
    #     readonly=True
    # )

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
    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'), default=0.0)
    tax_id = fields.Many2many('account.tax', related="product_id.taxes_id",string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True)

    ko_notes_ids = fields.Many2many('kitchen.order.notes', 'sale_workflow_cakeshop_kitchen_order_notes_', string='KO Notes')
    order_message_id = fields.Many2one('kitchen.message', string='Message')
    
    # Add manual price during order
    manual_price = fields.Float(string="Manual Price", digits=dp.get_precision('Manual Price'))

    # Product Addons Line
    product_addon_lines = fields.One2many('product.addons.line', 'product_config_soko', string="Addon Lines")

    # Compute unit price
    @api.depends('product_id', 'product_addon_lines')
    def _compute_price(self):
        self.price_unit = self.product_id.list_price
    
    # Compute total price
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'manual_price', 'product_addon_lines')
    def _compute_amount(self):

        for line in self:
            if line.manual_price:
                price = line.manual_price * (1 - (line.discount or 0.0) / 100.0)
            else:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            
            addon_price = 0.0
            if line.product_addon_lines:
                for addon in line.product_addon_lines:
                    addon_price += addon.amount

                price *= line.product_uom_qty
                price += addon_price
                price /= line.product_uom_qty
            
            taxes = line.tax_id.compute_all(price, line.currency_id, line.product_uom_qty, product=line.product_id, partner=line.partner_id)
            line.update({
                'price_total': taxes['total_included'],
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
            notes += "\n\nAddons:\n"
            for addon in self.product_addon_lines:
                notes += "- "
                notes += addon.product_id.name
                notes += " x" + str(int(addon.quantity))
                notes += "\n"

        ko_vals = {
            'product_id': self.product_id.id,
            'requested_date': self.requested_date,
            # 'pricelist_id': self.partner_id.property_product_pricelist.id,
            'saleorder_id': self.order_id.id,
            'name_for_message': self.name_for_message or '',
            'ko_note': notes,
            'ko_notes_ids': self.ko_notes_ids,
            'product_uom_qty': self.product_uom_qty,
            'company_id': self.company_id.id,
            'message_id': self.order_message_id.id
            # 'user_id': self.user_id and self.user_id.id,
            # 'team_id': self.team_id.id
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
            # 'client_order_ref': self.client_order_ref or '',
            'partner_id': self.partner_id.id,
            'requested_date': self.requested_date,
            # 'pricelist_id': self.partner_id.property_product_pricelist.id,
            # 'note': self.name_for_message,
            # 'payment_term_id': self.payment_term_id.id,
            'company_id': self.company_id.id,
            # 'user_id': self.user_id and self.user_id.id,
            # 'team_id': self.team_id.id
            'kitchen_sale_order_print_selection': self.kitchen_sale_order_print_selection
        }
        return order_vals

    @api.multi
    def _prepare_payment(self):
        """
        Prepare the dict of values to create the new payment for a advance payment. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        payment_methods = self.journal_id.inbound_payment_method_ids
        payment_method_id = payment_methods and payment_methods[0] or False
        payment_vals = {
            'payment_method_id': payment_method_id.id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner_id.id,
            'amount': self.amount,
            'journal_id': self.journal_id.id,
            'payment_date': self.payment_date,
            'communication': 'Advance Payement for order no %s' % self.order_id.name,
            'company_id': self.company_id.id,
            # 'user_id': self.user_id and self.user_id.id,
        }
        return payment_vals

    def _get_order_line_vals(self, product_id):
        """Hook to allow custom line values to be put on the newly
        created or edited lines."""
        product = self.env['product.product'].browse(product_id)
        
        # Add addon description and price unit in orderline
        orderline_desc = product.name or ""
        addon_price = 0.0

        if self.product_addon_lines:
            for addon in self.product_addon_lines:
                orderline_desc += " | "
                orderline_desc += addon.product_id.name
                
                addon_price += addon.amount
                    
            self.price_unit *= self.product_uom_qty
            self.price_unit += addon_price
            self.price_unit /= self.product_uom_qty
        
        return {
            'product_id': product_id,
            'name': orderline_desc,
            'price_unit': self.manual_price if self.manual_price else self.price_unit,
            'product_uom_qty': self.product_uom_qty,
            'product_uom': product.uom_id.id,
            'discount': self.discount,
            # 'tax_id': self.tax_id,
        }

    @api.multi
    def action_order_config_done(self):
        """Parse values and execute final code before closing the wizard"""
        # Create Order)

        # Check if manual price is less than the computed unit price
        if self.manual_price and self.manual_price < self.price_unit:
            raise UserError(_('Manual price cannot be set less than the Standard Price.\n Please check Manual Price again !'))

        SaleOrder = self.env['sale.order']
        sale_order = SaleOrder.create(self._prepare_order())
        sale_order.action_confirm()
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
            payment = Payment.create(self._prepare_payment())
            payment.post()
            self.payment_id = payment
            sale_order.payment_id = payment

        # sale order form view reference
        sale_order_form_ref_id = self.env.ref('sale.view_order_form').id

        # Do other works here
        return {
            'name': _('Sale Order'),
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'views': [(sale_order_form_ref_id, 'form')],
            'type': 'ir.actions.act_window'
        }


class ProductAddonsLine(models.TransientModel):
    _name = "product.addons.line"
    _description = 'Product Addon Line'
    _order = 'product_id, sequence, id'
    
    sequence = fields.Integer(string='Sequence', default=10)
    product_config_soko = fields.Many2one('product.configurator.ordernow.ko', string="Product Config SOKO")
    product_id = fields.Many2one('product.product', string="Addon", domain="[('is_addon', '=', True)]")
    quantity = fields.Float(string='Qty', default=1.0)
    uom_id = fields.Many2one(related="product_id.uom_id", string="UOM")
    unit_price = fields.Float(string='Rate')
    amount = fields.Float(string='Amount', compute="_compute_addon_amount")

    @api.depends('quantity', 'unit_price')
    def _compute_addon_amount(self):
        for addon in self:
            if addon.quantity and addon.unit_price:
                addon.amount = addon.quantity * addon.unit_price
            else:
                addon.amount = 0.0
