# -*- coding: utf-8 -*-

from odoo import api, fields, models, api, _
from odoo.exceptions import Warning, ValidationError
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
        string="Partner"
    )

    requested_date = fields.Datetime(string='Requested Date', required=True, index=True, copy=False, default=fields.Datetime.now)
    client_order_ref = fields.Char(string='Customer Reference', copy=False)
    amount = fields.Monetary(string='Advance Amount', required=True, default=0)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    journal_id = fields.Many2one('account.journal', string='Payment Journal', domain=[('type', 'in', ('bank', 'cash'))])
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)

    @api.multi
    def _prepare_order(self):
        """
        Prepare the dict of values to create the new order for a new order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        order_vals = {
            'client_order_ref': self.client_order_ref or '',
            'partner_id': self.partner_id.id,
            'requested_date': self.requested_date,
            # 'pricelist_id': self.partner_id.property_product_pricelist.id,
            'note': self.client_order_ref,
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
        payment_vals = {
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
            'product_uom': product.uom_id.id,
        }

    @api.multi
    def action_order_config_done(self):
        """Parse values and execute final code before closing the wizard"""
        # try:
        #     variant = self.config_session_id.create_get_variant()
        # except ValidationError:
        #     raise
        # except Exception:
        #     raise ValidationError(
        #         _('Invalid configuration! Please check all '
        #           'required steps and fields.')
        #     )
        # Create Order
        _logger.error("Order config done")
        SaleOrder = self.env['sale.order']
        sale_order = SaleOrder.create(self._prepare_order())
        self.order_id = sale_order

        # Attach sale order line
        line_vals = self._get_order_line_vals(self.product_id.id)
        # if self.order_line_id:
        #   self.order_line_id.write(line_vals)
        # else:
        self.order_id.write({'order_line': [(0, 0, line_vals)]})
        
        # Create Payment if any
        Payment = self.env['account.payment']
        payment = Payment.create(self._prepare_payment())
        payment.post()
        self.payment_id = payment
        _logger.error("Order config doneasdfas")
        # Create Kitchen Order


        # Do other works here
        return

class ProductConfiguratorSaleOrderNow(models.TransientModel):
    _name = 'product.configurator.ordernow'
    _inherit = 'product.configurator'

    @api.multi
    def configure_order(self, product_id):
        _logger.error("Product id after config is: %s" % str(product_id))
        product = self.env['product.product'].browse(product_id)
        order_configurator_view_id = self.env.ref('sale_workflow_cakeshop.product_configurator_ordernow_ko_form').id
        _logger.error(product_id)
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
                default_product_id=product_id,
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
