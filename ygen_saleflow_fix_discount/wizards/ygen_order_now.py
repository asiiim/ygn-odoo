# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, api, _
from odoo.exceptions import Warning, ValidationError, UserError

from odoo.addons import decimal_precision as dp

import logging

_logger = logging.getLogger(__name__)


class YgenOrderNow(models.TransientModel):
    _inherit = 'ygen.order.now'

    fix_discount = fields.Float(string='Fixed Discount', default=0.0)

    # Overrride Compute total price
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'manual_price', 'addon_lines', 'fix_discount')
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

            elif line.fix_discount:
                unit_non_extra_price -= (line.fix_discount / line.product_uom_qty)

            taxes = line.tax_id.compute_all(unit_non_extra_price, line.currency_id, line.product_uom_qty, product=line.prd_id, partner=line.partner_id)
            
            line.update({
                'price_total': taxes['total_included'] + extra_prd_price
            })
        
    # Override Orderline Vals Return Method
    def _get_order_line_vals(self, product):
        """Hook to allow custom line values to be put on the newly
        created or edited lines."""
        
        # Add addon description and price unit in orderline
        orderline_desc = product.name or ""
        addon_price = 0.0
        discount = 0.0
        fix_discount = 0.0
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
        elif self.fix_discount:
            fix_discount = self.fix_discount / self.product_uom_qty
        
        return {
            'product_id': product.id,
            'name': orderline_desc,
            'price_unit': self.manual_price if self.manual_price else self.price_unit,
            'product_uom_qty': self.product_uom_qty,
            'product_uom': product.uom_id.id,
            'discount': discount,
            'discount_fixed': fix_discount,
            'uom_name': product.uom_id.name,
            'addon_details': addon_details
        }

    # Override Order Now Methods
    @api.multi
    def action_order_config_done(self):

        self.ensure_one()
        order_done = super(YgenOrderNow, self).action_order_config_done()

        # Log fix discount if provided
        msg = ""
        if self.fix_discount:
            msg += "<br/><b>Fix Discount</b><br/>"
            msg += "<li>" + str(self.fix_discount) + "/-"
            
        self.order_id.message_post(body=msg)
        return order_done

    @api.multi
    def action_new_order_config_done(self):

        self.ensure_one()
        order_done = super(YgenOrderNow, self).action_new_order_config_done()

        # Log fix discount if provided
        msg = ""
        if self.fix_discount:
            msg += "<br/><b>Fix Discount</b><br/>"
            msg += "<li>" + str(self.fix_discount) + "/-"
            
        self.order_id.message_post(body=msg)
        return order_done

    