# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import Warning, ValidationError, UserError

import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Validate Stock Picking Operation
    delivery_validated = fields.Boolean('Delivery Validated?', default=False, readonly=True, copy=False, track_visibility='onchange')

    @api.multi
    def validate_picking(self):
        for so in self:
            stock_pickings = so.mapped('picking_ids').filtered(lambda r: r.state != 'cancel')
            # stock_pickings = self.env['stock.picking'].search([('origin', '=', so.name), ('state', '!=', 'cancel')])
            if stock_pickings:
                for stock_picking in stock_pickings:
                    _logger.warning(stock_picking.state)
                    if stock_picking.state not in ["done", "cancel"]:
                        _logger.warning(stock_picking.state)
                        stock_picking.button_validate()
                    so.write({'delivery_validated': True})
            else:
                raise UserError(_('No such deliveries to validate.'))

    @api.multi
    def action_order_new(self):
        """Return action to start new order now wizard"""
        self.ensure_one()
        
        order_configurator_view_id = self.env.ref('ygen_sale_order_flow.ygen_order_now_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ygen.order.now',
            'name': "Order Configurator",
            'view_mode': 'form',
            'view_id': order_configurator_view_id,
            'target': 'new',
            'context': dict(
                self.env.context,
                wizard_model='ygen.order.now'
            ),
        }

    @api.multi
    def view_sale_order(self):
        sale_order_form_ref_id = self.env.ref('ygen_sale_order_flow.preview_order_form').id
        return {
            'name': _('Sale Order'),
            'res_model': 'sale.order',
            'res_id': self.id,
            'views': [(sale_order_form_ref_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    # Change requested date
    @api.multi
    def action_change_requested_date(self):
        """Return action to change the requested date"""
        sale_requested_date_view_id = self.env.ref('ygen_sale_order_flow.sale_change_requested_date_form').id
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

    # Change customer
    @api.multi
    def action_change_customer(self):
        """Return action to change the customer"""
        sale_customer_view_id = self.env.ref('ygen_sale_order_flow.sale_change_partner_form').id
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

    # Provide Reference Product
    ref_product_id = fields.Many2one(comodel_name='product.product', string='Reference Product', domain="[('sale_ok', '=', True), ('is_custom', '=', False), ('is_addon', '=', False)]")

    # Edit sale order
    @api.multi
    def action_edit_sale_order(self):
        order_configurator_view_id = self.env.ref('ygen_sale_order_flow.ygen_order_now_edit_form').id

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ygen.order.now',
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
                wizard_model='ygen.order.now',
            ),
        }

    # Make sale order
    @api.multi
    def action_make_order(self):
        self.ensure_one()
        order_make_view_id = self.env.ref('ygen_sale_order_flow.make_order_form').id
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
