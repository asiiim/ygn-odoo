# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, api, _
from odoo.exceptions import Warning, ValidationError, UserError

from odoo.addons import decimal_precision as dp

import logging

_logger = logging.getLogger(__name__)


class YgenOrderNow(models.TransientModel):
    _inherit = 'ygen.order.now'


    order_message_id = fields.Many2one('kitchen.message', string='Message')
    name_for_message = fields.Char(string="Name for Message", copy=False)
    ko_notes_ids = fields.Many2many('kitchen.order.notes', 'ygen_sale_order_flow_kitchen_order_notes_', string='KO Notes')
    ko_note = fields.Text(string="KO Note", track_visibility='onchange')

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
        if self.addon_lines:
            notes += "\nAddons:\n"
            for addon in self.addon_lines:
                if addon.is_addon:
                    notes += "- "
                    notes += addon.addon_id.name
                    notes += " x" + str(int(addon.quantity))
                    notes += "\n"

        ko_vals = {
            'product_id': self.prd_id.id,
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
        order_vals = super(YgenOrderNow, self)._prepare_order()
        order_vals.update({'kitchen_sale_order_print_selection': self.kitchen_sale_order_print_selection})
        return order_vals

    @api.multi
    def action_order_config_done(self):
        """Parse values and execute final code before closing the wizard"""

        order_done = super(YgenOrderNow, self).action_order_config_done()

        # Check sale order from the context
        if not self.order_id:
            # Create Kitchen Order
            KitchenOrder = self.env['kitchen.order']
            KitchenOrder.create(self._prepare_kitchen_order())
        else:
            # Changes in KO
            ko_vals = self._prepare_kitchen_order()
            if self.order_id.kitchen_order_ids:
                for ko in self.order_id.kitchen_order_ids:
                    ko.write({
                        'product_uom_qty': ko_vals.get('product_uom_qty'),
                        'ko_note': ko_vals.get('ko_note'),
                        'ref_product_id': self.ref_product_id.id
                    })
                    ko.start_kitchen_order()
                    break 
            else:
                # Create Kitchen Order
                KitchenOrder = self.env['kitchen.order']
                KitchenOrder.create(self._prepare_kitchen_order())
        return order_done

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
            'views': [(self.env.ref('ygen_sale_kitchen_workflow.kitchen_order_form_inherit').id, 'form')],
            'type': 'ir.actions.act_window',
            'target':'new'
        }

    @api.multi
    def action_new_order_config_done(self):
        """Parse values and execute final code before closing the wizard"""

        super(YgenOrderNow, self).action_new_order_config_done()

        # Create Kitchen Order
        KitchenOrder = self.env['kitchen.order']
        KitchenOrder.create(self._prepare_kitchen_order())
        
        return self.view_order_description()
