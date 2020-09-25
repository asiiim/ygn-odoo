# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, api, _
from odoo.exceptions import Warning, ValidationError, UserError

from odoo.addons import decimal_precision as dp

import logging

_logger = logging.getLogger(__name__)


class YgenOrderNow(models.TransientModel):
    _name = 'ygen.order.now'

    prd_id = fields.Many2one(comodel_name='product.product', string='Product', domain="[('sale_ok', '=', True), ('is_custom', '=', True)]", required=True)
    product_uom_id = fields.Many2one(related='prd_id.uom_id', readonly=True)
    uom = fields.Char(related='product_uom_id.name', string='UOM')
    
    order_id = fields.Many2one(comodel_name='sale.order', readonly=True)
    saleorder_date = fields.Datetime(string='Order Date', required=True, index=True, copy=False, default=fields.Datetime.now)
    partner_id = fields.Many2one(comodel_name='res.partner', string="Customer")

    requested_date = fields.Datetime(string='Requested Date', required=True, index=True, copy=False)
    # client_order_ref = fields.Char(string='Customer Reference', copy=False)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)

    journal_id = fields.Many2one('account.journal', string='Payment Journal', domain=[('type', 'in', ('bank', 'cash'))], default=lambda self: self.env['account.journal'].search([('type', '=', 'cash')], limit=1))
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
    price_unit = fields.Float(string="Price", digits=dp.get_precision('Unit Price'), oldname="price", compute="_compute_price")
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    
    # discount styles
    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'), default=0.0)
    
    tax_id = fields.Many2many('account.tax', related="prd_id.taxes_id",string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True)
    
    # Add manual price during order
    manual_price = fields.Float(string="Manual Price", digits=dp.get_precision('Manual Price'))

    # Product Addons Line
    addon_lines = fields.One2many('ygen.order.addons', 'ygen_order_id', string="Addon Lines")

    # Sales Channel In Wizard
    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()
    
    team_id = fields.Many2one('crm.team', 'Sales Channel', change_default=True, default=_get_default_team, oldname='section_id')

    # Compute unit price
    @api.depends('prd_id', 'addon_lines')
    def _compute_price(self):
        self.price_unit = self.prd_id.list_price
    
    # Compute total price
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'manual_price', 'addon_lines')
    def _compute_amount(self):

        # Extra product price
        extra_prd_price = 0.0
        price = 0.0
        unit_non_extra_price = 0.0
        addon_price = 0.0

        for line in self:

            # check if it has unit price or manual price
            if line.manual_price:
                unit_non_extra_price = line.manual_price
            else:
                unit_non_extra_price = line.price_unit

            # check if product addons are selected
            if line.addon_lines:
                for addon in line.addon_lines:

                    # Sum up extra product price else add addons only
                    if addon.is_extra:
                        extra_prd_price += addon.amount
                    else:
                        addon_price += addon.amount

                price = unit_non_extra_price
                price *= line.product_uom_qty
                price += addon_price
                unit_non_extra_price = price / line.product_uom_qty
            
            # apply discount if provided
            if line.discount:
                unit_non_extra_price *= (1 - (line.discount or 0.0) / 100.0)

            taxes = line.tax_id.compute_all(unit_non_extra_price, line.currency_id, line.product_uom_qty, product=line.prd_id, partner=line.partner_id)

            line.update({
                'price_total': taxes['total_included'] + extra_prd_price
            })

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
            'company_id': self.company_id.id
        }
        return order_vals

    def _get_extra_product_vals(self, addon):
        return {
            'product_id': addon.addon_id.id,
            'name': addon.addon_id.name,
            'price_unit': addon.unit_price,
            'product_uom_qty': addon.quantity,
            'product_uom': addon.addon_id.uom_id.id,
            'uom_name': addon.addon_id.uom_id.name
        }

    def _get_order_line_vals(self, product):
        """Hook to allow custom line values to be put on the newly
        created or edited lines."""
        
        # Add addon description and price unit in orderline
        orderline_desc = product.name or ""
        addon_price = 0.0
        discount = 0.0
        addon_details = ""

        if self.addon_lines:
            for addon in self.addon_lines:
                if addon.is_addon:
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
        
        return {
            'product_id': product.id,
            'name': orderline_desc,
            'price_unit': self.manual_price if self.manual_price else self.price_unit,
            'product_uom_qty': self.product_uom_qty,
            'product_uom': product.uom_id.id,
            'discount': discount,
            'uom_name': product.uom_id.name,
            'addon_details': addon_details
        }

    @api.multi
    def action_order_config_done(self):
        """Parse values and execute final code before closing the wizard"""

        self.ensure_one()

        # Check if manual price is less than the computed unit price
        if self.manual_price and self.manual_price < self.price_unit:
            raise UserError(_('Manual price cannot be set less than the Standard Price.\n Please check Manual Price again !'))

        # Check sale order from the context
        if not self.order_id:
            SaleOrder = self.env['sale.order']
            sale_order = SaleOrder.create(self._prepare_order())
            self.order_id = sale_order

            # Attach sale order line
            order_lines = [(5, 0, 0)]
            line_vals = self._get_order_line_vals(self.prd_id)
            order_lines.append((0, 0, line_vals))

            # Attach Extra Products if present in Addon Lines
            if self.addon_lines:
                for addon in self.addon_lines:
                    if addon.is_extra:
                        vals = self._get_extra_product_vals(addon)
                        order_lines.append((0, 0, vals))

            sale_order.order_line = order_lines
            sale_order.order_line._compute_tax_id()

            # Confirm Sale Order
            sale_order.action_confirm()

            # sale order form view reference
            sale_order_form_ref_id = self.env.ref('sale.view_order_form').id

            # Log the sale order details in the chatter
            msg = "<b>Order Details</b><br/>"
            msg += "<li>Product: " + str(line_vals.get('name')) + "<br/>"
            msg += "<li>Qty: " + str(line_vals.get('product_uom_qty')) + " " + str(line_vals.get('uom_name')) + "<br/>"
            
            if line_vals.get('addon_details'):
                msg += "<br/><b>Addons Details</b><br/>"
                msg += str(line_vals.get('addon_details'))

            if self.discount:
                msg += "<br/><b>Discount</b><br/>"
                msg += "<li>" + str(self.discount) + "%"
            
            self.order_id.message_post(body=msg)

            # Show sale order form view
            return {
                'name': _('Sale Order'),
                'res_model': 'sale.order',
                'res_id': self.order_id.id,
                'views': [(sale_order_form_ref_id, 'form')],
                'type': 'ir.actions.act_window'
            }

        # Else part of this code is for editing the created sale order in the wizard.
        else:
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
            # Empty set to callect orderline vals
            order_lines = [(5, 0, 0)]

            # Remove all orderlines from the sale order
            self.order_id.order_line = [(5, 0, 0)]

            line_vals = self._get_order_line_vals(self.prd_id)
            order_lines.append((0, 0, line_vals))

            # Attach Extra Products if present in Addon Lines
            if self.addon_lines:
                for addon in self.addon_lines:
                    if addon.is_extra:
                        vals = self._get_extra_product_vals(addon)
                        order_lines.append((0, 0, vals))
            
            self.order_id.order_line = order_lines
            self.order_id.order_line._compute_tax_id()

            
            # Confirm the sale order
            self.order_id.action_confirm()

            # Log the sale order details in the chatter
            orderline_vals = self._get_order_line_vals(self.prd)
            msg = "<b>Order Details</b><br/>"
            msg += "<li>Product: " + str(orderline_vals.get('name')) + "<br/>"
            msg += "<li>Qty: " + str(orderline_vals.get('product_uom_qty')) + " " + str(orderline_vals.get('uom_name')) + "<br/>"
            
            if self.addon_lines:
                msg += "<br/><b>Addons Details</b><br/>"
                msg += str(orderline_vals.get('addon_details'))

            if self.discount:
                msg += "<br/><b>Discount</b><br/>"
                msg += "<li>" + str(self.discount) + "%"
            
            self.order_id.message_post(body=msg)
            return

    
    @api.multi
    def action_new_order_config_done(self):

        self.ensure_one()

        # Check if manual price is less than the computed unit price
        if self.manual_price and self.manual_price < self.price_unit:
            raise UserError(_('Manual price cannot be set less than the Standard Price.\n Please check Manual Price again !'))

        SaleOrder = self.env['sale.order']
        sale_order = SaleOrder.create(self._prepare_order())
        self.order_id = sale_order

        # Attach sale order line
        order_lines = [(5, 0, 0)]
        line_vals = self._get_order_line_vals(self.prd_id)
        order_lines.append((0, 0, line_vals))

        # Attach Extra Products if present in Addon Lines
        if self.addon_lines:
            for addon in self.addon_lines:
                if addon.is_extra:
                    vals = self._get_extra_product_vals(addon)
                    order_lines.append((0, 0, vals))
        
        sale_order.order_line = order_lines
        sale_order.order_line._compute_tax_id()

        # Confirm sale order
        sale_order.action_confirm()

        # Log the sale order details in the chatter
        msg = "<b>Order Details</b><br/>"
        msg += "<li>Product: " + str(line_vals.get('name')) + "<br/>"
        msg += "<li>Qty: " + str(line_vals.get('product_uom_qty')) + " " + str(line_vals.get('uom_name')) + "<br/>"
        
        if line_vals.get('addon_details'):
            msg += "<br/><b>Addons Details</b><br/>"
            msg += str(line_vals.get('addon_details'))

        if self.discount:
            msg += "<br/><b>Discount</b><br/>"
            msg += "<li>" + str(self.discount) + "%"
        
        self.order_id.message_post(body=msg)

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

    # Provide Reference Product
    ref_product_id = fields.Many2one(comodel_name='product.product', string='Reference Product', domain="[('sale_ok', '=', True), ('is_custom', '=', False), ('is_addon', '=', False), ('is_extra', '=', False)]")

class YgenOrderAddons(models.TransientModel):
    _name = "ygen.order.addons"
    _description = 'Ygen Order Addons'
    _order = 'addon_id, sequence, id'
    
    sequence = fields.Integer(string='Sequence', default=10)
    ygen_order_id = fields.Many2one('ygen.order.now', string="Order Wizard")
    addon_id = fields.Many2one('product.product', string="Addon", domain="['|', ('is_addon', '=', True), ('is_extra', '=', True), ('sale_ok', '=', True)]", ondelete='restrict', required=True, oldname="product_id")
    is_addon = fields.Boolean('Is Addon', related="addon_id.is_addon")
    is_extra = fields.Boolean('Is Extra', related="addon_id.is_extra")

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
