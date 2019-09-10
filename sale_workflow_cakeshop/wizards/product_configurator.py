# -*- coding: utf-8 -*-

from odoo import api, fields, models, api, _
from odoo.exceptions import Warning, ValidationError

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

    requested_date = fields.Datetime(string='Requested Date', required=True, index=True, copy=False, default=fields.Datetime.now)
    order_description = fields.Text(string="Order Description", copy=False)
    ko_note = fields.Text(string="KO Note", track_visibility='onchange')
    client_order_ref = fields.Char(string='Customer Reference', copy=False)
    amount = fields.Monetary(string='Advance Amount', required=True, default=0)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    journal_id = fields.Many2one('account.journal', string='Payment Journal', domain=[('type', 'in', ('bank', 'cash'))])
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
    price_unit = fields.Float(related="product_id.lst_price", string="Price", digits=dp.get_precision('Unit Price'), oldname="price")
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'), default=0.0)
    tax_id = fields.Many2many('account.tax', related="product_id.taxes_id",string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True)

    ko_notes_ids = fields.Many2many('kitchen.order.notes', 'sale_workflow_cakeshop_kitchen_order_notes_', string='KO Notes')
    
    @api.depends('product_uom_qty', 'discount', 'price_unit')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
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
            notes = notes + note.name + "\n"
        notes = notes + self.ko_note or ''

        ko_vals = {
            'product_id': self.product_id.id,
            'requested_date': self.requested_date,
            # 'pricelist_id': self.partner_id.property_product_pricelist.id,
            'saleorder_id': self.order_id.id,
            'order_description': self.order_description or '',
            'ko_note': notes,
            'ko_notes_ids': self.ko_notes_ids,
            'product_uom_qty': self.product_uom_qty,
            'company_id': self.company_id.id,
            # 'user_id': self.user_id and self.user_id.id,
            # 'team_id': self.team_id.id
        }
        return ko_vals

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
            'note': self.order_description,
            # 'payment_term_id': self.payment_term_id.id,
            'company_id': self.company_id.id,
            # 'user_id': self.user_id and self.user_id.id,
            # 'team_id': self.team_id.id
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

        return {
            'product_id': product_id,
            'name': product._get_mako_tmpl_name(),
            'price_unit': self.price_unit,
            'product_uom_qty': self.product_uom_qty,
            'product_uom': product.uom_id.id,
            'discount': self.discount,
            # 'tax_id': self.tax_id,
        }

    @api.multi
    def action_order_config_done(self):
        """Parse values and execute final code before closing the wizard"""
        # Create Order)
        SaleOrder = self.env['sale.order']
        sale_order = SaleOrder.create(self._prepare_order())
        sale_order.action_confirm()
        self.order_id = sale_order

        # Attach sale order line
        line_vals = self._get_order_line_vals(self.product_id.id)
        self.order_id.write({'order_line': [(0, 0, line_vals)]})
        
        # Create Kitchen Order
        KitchenOrder = self.env['kitchen.order']
        kitchen_order = KitchenOrder.create(self._prepare_kitchen_order())
        
        # Create Payment if any
        Payment = self.env['account.payment']
        payment = Payment.create(self._prepare_payment())
        payment.post()
        self.payment_id = payment
        

        # Do other works here
        return sale_order

class ProductConfiguratorSaleOrderNow(models.TransientModel):
    _name = 'product.configurator.ordernow'
    _inherit = 'product.configurator'

    @api.multi
    def configure_order(self, product_id):
        product = self.env['product.product'].browse(product_id)
        order_configurator_view_id = self.env.ref('sale_workflow_cakeshop.product_configurator_ordernow_ko_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.configurator.ordernow.ko',
            'name': "Order Configurator",
            'view_mode': 'form',
            'view_id': order_configurator_view_id,
            'target': 'new',
            'context': dict(
                self.env.context,
                default_product_tmpl_id=product.product_tmpl_id.id,
                default_product_id=product.id,
                wizard_model='product.configurator.ordernow.ko',
            ),
        }
    
    @api.multi
    def action_config_done(self):
        """Parse values and execute final code before closing the wizard"""
        res = super(ProductConfiguratorSaleOrderNow, self).action_config_done()
        _logger.error("res id after config is: %s" % str(res['res_id']))
        # Call order configurator wizard
        return self.configure_order(res['res_id'])
