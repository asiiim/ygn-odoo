# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import UserError
from odoo import models, fields, api, _

from pyparsing import (Literal, CaselessLiteral, Word, Combine, Group, Optional,
                       ZeroOrMore, Forward, nums, alphas, oneOf)
import math
import operator
import datetime
import logging

_logger = logging.getLogger(__name__)

STORAGE_PARAM = ('length', 'breadth', 'height', 'diameter', 'pi', 'dip')

class Location(models.Model):
    _inherit = 'stock.location'

    length = fields.Float(string="Length (in meter)", help="Length of the Storage.", default=0.0)
    breadth = fields.Float(string="Breadth (in meter)", help="Breadth of the Storage.", default=0.0)
    height = fields.Float(string="Height (in meter)", help="Height of the Storage.", default=0.0)
    diameter = fields.Float(string="Diameter (in meter)", help="Diameter of the Storage.", default=0.0)
    pi = fields.Float(string="PI", default=3.142857142857143)

    is_length = fields.Boolean(default=False)
    is_breadth = fields.Boolean(default=False)
    is_height = fields.Boolean(default=False)
    is_diameter = fields.Boolean(default=False)

    formula_id = fields.Many2one('storage.category', string="Storage Category")
    volume = fields.Float(string="Volume (in Kilolitre)", help="Volume of the Storage.", store=True)
    color = fields.Integer('Color')
    is_station = fields.Boolean(string='Station', default=False)

    max_shrinkage_loss = fields.Float(string="Maximum Shrinkage Loss", default=0.0)

    @api.model
    def _param_fields(self):
        """Returns the list of param fields."""
        return list(STORAGE_PARAM)

    @api.multi
    def calc_volume(self):

        '''
        The purpose of this function is to calculate the volume of the storage.

        :param address: browse record of the storage.category for the formula and parameter
        :returns: volume of the storage
        :rtype: float
        '''
        # get the information that will be injected into the volume calculation
        # get the formula

        for location in self:
            formula_format = location.formula_id.formula
            if formula_format:
                args = {
                    'length': location.length or 0.0,
                    'breadth': location.breadth or 0.0,
                    'height': location.height or 0.0,
                    'diameter': location.diameter or 0.0,
                    'pi': location.pi or 0.0,
                }

                for field in location._param_fields():
                    if field:
                        args[field] = getattr(location, field) or ''
                
                try:
                    result = eval(str(formula_format % args))
                    location.volume = result
                    return result
                except:
                    raise UserError(_("Please set the parameter values rather than 0.0 !"))

    
    ############################################################################################


    meter_reading = fields.Float(string="Meter Reading")
    sold_qty = fields.Float(string="Current Sold Quantity (in Liter)", default=0.0)
    shrinkage_value = fields.Float(string="Shrinkage Value")
    product_quantity = fields.Float(related="quant_ids.quantity", string="On Hand")
    dip = fields.Float(string="Dip Value (in meter)", help="Value of the Dip Test.", default=0.0)
    is_dip = fields.Boolean(default=False)
    filled_volume = fields.Float(string="Remaining Volume (in Kilolitre)", help="Remaining 'Volume in the storage.")

    product_id = fields.Many2one('product.product', 'Inventoried Product', help="Specify Product to focus your inventory on a particular Product.")
    # product_uom = fields.Many2one('product.uom', 'Station Product of Measure')

    is_product_filter = fields.Boolean('Is Filter = "product"', default=False)
    
    
    @api.multi
    @api.depends('formula_id', 'dip')
    def _calc_filled_volume(self):

        '''
        The purpose of this function is to calculate the filled volume of the storage by the dip value obtained from.

        :param address: browse record of the storage.category for the formula and parameter
        :returns: filled volume of the storage
        :rtype: float
        '''
        # get the information that will be injected into the filled volume calculation
        # get the formula

        on_hand = 0.0

        for location in self:
            formula_format = location.formula_id.diptest_formula
            if formula_format and self.dip:
                args = {
                    'length': location.length or 0.0,
                    'breadth': location.breadth or 0.0,
                    'height': location.height or 0.0,
                    'diameter': location.diameter or 0.0,
                    'pi': location.pi or 0.0,
                    'dip': location.dip or 0.0,
                }

                for field in self._param_fields():
                    if field:
                        args[field] = getattr(location, field) or ''

                on_hand = eval(str(formula_format % args))
                self.write({'filled_volume': on_hand})
                self.check_product_onhand(on_hand)
                return on_hand
            else:
                self.write({'filled_volume': 0.0})
                self.check_product_onhand(on_hand)
                return on_hand

    def check_product_onhand(self, qty):

        if qty > self.volume:
            raise UserError(_("Quantity On Hand exceeds the storage capacity. \nPerform the test again with correct Dip Value."))
        
        # if qty > self.product_quantity:
        #     raise UserError(_("Quantity from Dip Test is greater than the quantity On Hand."))

        max_shrinkage_loss = self.env.user.company_id.max_shrinkage_loss or 0.0
        shrinkage_value = abs((qty * 1000) - self.product_quantity)
        
        if shrinkage_value >= max_shrinkage_loss:
            # to discuss: does the shrinkage field take latest value or append the value?
            if self.product_quantity > (qty * 1000):
                self.write({'shrinkage_value': shrinkage_value})
            self._make_inv_adjustment(qty)
    
    @api.multi
    def _make_inv_adjustment(self, qty):

        vals = {
            'name': "[IA] " + str(self.name),
            'filter': 'product',
            'state': 'draft',
            'location_id':  self.id,
            'product_id': self.product_id.id,
        }

        inv_adjust = self.env['stock.inventory'].create(vals)
        inv_adjust.action_start()
        line_ids = self.env['stock.inventory.line'].search([('inventory_id', '=', inv_adjust.id)])
        qty_liter = qty * 1000

        if line_ids:
            for line in line_ids:
                line.write({ 'product_qty': qty_liter })
        else:
            vals = {
                'inventory_id': inv_adjust.id,
                'location_id': self.id,
                'product_id': self.product_id.id,
                'product_qty': qty_liter,
                'theoretical_qty': qty_liter
            }
            line = self.env['stock.inventory.line'].create(vals)
        inv_adjust.action_done()

    def _get_action(self, action_xmlid):
        action = self.env.ref(action_xmlid).read()[0]
        if self:
            action['dip'] = self.dip
        return action

    def get_diptest_wizard_action(self):
        return self._get_action('station.diptest_wizard_action')

    def get_quick_sale_wizard_action(self):
        return self._get_action('station.quick_sale_wizard_action')

    @api.multi
    def close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def edit_dialog(self):
        form_view = self.env.ref('stock.view_location_form')
        return {
            'name': _('Location'),
            'res_model': 'stock.location',
            'res_id': self.id,
            'views': [(form_view.id, 'form'),],
            'type': 'ir.actions.act_window',
            'target': 'inline'
        }

    @api.multi
    @api.depends('formula_id')
    def _set_volume_param(self, formula_id):

        '''
        The purpose of this function is to set the param for the storage calculations on the
        basis of the chosen formula format.

        :param address: formula format from the active location in the context
        :returns: set the boolean for the param
        :rtype: bool
        '''

        length = False
        breadth = False
        height = False
        diameter = False
        
        formula_format = self.env['storage.category'].search([('id', '=', formula_id)]).formula
        if formula_format:
            if "length" in formula_format: length = True
            if "breadth" in formula_format: breadth = True
            if "height" in formula_format: height = True
            if "diameter" in formula_format: diameter = True
        
        vals = {
            'is_length': length,
            'is_breadth': breadth,
            'is_height': height,
            'is_diameter': diameter
        }

        return vals

    @api.model
    def create(self, vals):
        if 'location_id' in vals:
            vals['is_product_filter'] = True
            param_vals = self._set_volume_param(vals['formula_id'])
            vals.update(param_vals)
            
            return super(Location, self).create(vals)

    @api.onchange('formula_id')
    def _set_volume_param_onchange(self):

        length = False
        breadth = False
        height = False
        diameter = False
        is_station = False
        
        formula_format = self.formula_id.formula
        if formula_format:
            if "length" in formula_format: length = True
            if "breadth" in formula_format: breadth = True
            if "height" in formula_format: height = True
            if "diameter" in formula_format: diameter = True
            is_station = True
        
        self.is_length = length
        self.is_breadth = breadth
        self.is_height = height
        self.is_diameter = diameter
        self.is_station = is_station

# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

# method for confirming the quick sale which registers the payment in the account and maintains
# stocks in the inventory
    def confirm_quick_sale(self):
        
        for rec in self:
            if rec.sold_qty > 0:
                if rec.product_quantity == 0:
                    raise UserError(_("On hand quantity is empty."))

                if rec.sold_qty > rec.product_quantity:
                    raise UserError(_("Not Enough quantity for sale."))

                total = rec.sold_qty * rec.product_id.lst_price
                rec.meter_reading += rec.sold_qty
                journal = self.env['account.journal'].search([('name', '=', 'Cash')])
                now_datetime = datetime.datetime.now()

                memo = str(rec.product_id.name) + "/" + str(now_datetime.year) + "/" + str(now_datetime.month) + str(now_datetime.day) + str(now_datetime.hour) + str(now_datetime.minute) + str(now_datetime.second)

                ac_pay_vals = {
                    'amount': total,
                    'payment_date': now_datetime,
                    'journal_id': journal.id,
                    'communication': memo,
                    'payment_type': 'inbound',
                    'state': 'draft',
                    'currency_id': self.env.user.company_id.currency_id.id,
                    'payment_method_id': 1,
                    'partner_type': 'customer'
                }

                dest_loc = self.env['stock.location'].search([('name', '=', 'Customers'), ('usage', '=', 'customer')], limit=1)

                stock_move_line_vals = {
                    'name': '[MOVE] ' + memo,
                    'product_id': rec.product_id.id,
                    'quantity_done': rec.sold_qty,
                    'product_uom': rec.product_id.product_tmpl_id.uom_id.id
                }

                stock_pick_type = self.env['stock.picking.type'].search([('name', '=', 'Internal Transfers')], limit=1)

                if not stock_pick_type:
                    raise UserError(_("Multi Stock Location features is not available now.\nPlease go through the Settings > General Settings > Inventory > Storage Locations and \nbe sure to check this feature."))

                stock_pick_vals = {
                    'location_id': rec.id,
                    'location_dest_id': dest_loc.id,
                    'move_lines': [(0, 0, stock_move_line_vals)],
                    'picking_type_id': stock_pick_type.id,
                    'origin': "[PICK] " + memo,
                    'scheduled_date': now_datetime,
                    'state': 'draft'
                }

                stock_pick = self.env['stock.picking'].create(stock_pick_vals)
                stock_pick.button_validate()

                ac_pay = self.env['account.payment'].create(ac_pay_vals)
                return ac_pay.post()
