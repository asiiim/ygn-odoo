# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo import models, fields, api, _

from pyparsing import (Literal, CaselessLiteral, Word, Combine, Group, Optional,
                       ZeroOrMore, Forward, nums, alphas, oneOf)
import math
import operator

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
                    _logger.info(_("Please provide parameter value greater than 0.0"))

    
    ############################################################################################


    meter_reading = fields.Float(string="Meter Reading")
    shrinkage_value = fields.Float(string="Shrinkage Value")
    product_quantity = fields.Float(related="quant_ids.quantity", string="On Hand")
    dip = fields.Float(string="Dip Value (in meter)", help="Value of the Dip Test.", default=0.0)
    is_dip = fields.Boolean(default=False)
    filled_volume = fields.Float(compute="_calc_filled_volume", string="Remaining Volume (in Kilolitre)", help="Remaining 'Volume in the storage.", store=True)

    product_id = fields.Many2one('product.product', 'Inventoried Product', help="Specify Product to focus your inventory on a particular Product.")

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

        current_station = self.env['stock.location'].browse(self._context.get('active_id'))
        for station in current_station:
            station.write({'dip': self.dip})

        for location in current_station:
            formula_format = location.formula_id.diptest_formula
            if formula_format:
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
                try:
                    on_hand = eval(str(formula_format % args))
                    self.filled_volume = on_hand
                    self._make_inv_adjustment(on_hand, location)
                    return on_hand
                except:
                    _logger.info(_("Please provide parameter value greater than 0.0"))
                    # raise UserError(_("Please provide parameter value greater than 0.0"))
    
    @api.multi
    def _make_inv_adjustment(self, qty, location):
        vals = {
            'name': "[IA] " + str(location.name),
            'filter': 'product',
            'state': 'draft',
            'location_id':  location.id,
            'product_id': location.product_id.id,
        }
        inv_adjust = self.env['stock.inventory'].create(vals)
        inv_adjust.action_start()
        line_ids = self.env['stock.inventory.line'].search([('inventory_id', '=', inv_adjust.id)])

        if line_ids:
            for line in line_ids:
                line.write({ 'product_qty': qty })
        else:
            vals = {
                'inventory_id': inv_adjust.id,
                'location_id': location.id,
                'product_id': location.product_id.id,
                'product_qty': qty,
                'theoretical_qty': qty
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
        _logger.warning("Param Values ------------------------- " + str(vals))

        return vals

    @api.model
    def create(self, vals):
        _logger.warning("VALSSSSSSSSSSSS ------------------------ " + str(vals))
        if 'location_id' in vals:
            _logger.warning("VALSSSSSSSSSSSS ------------------------ " + str(vals))
            _logger.warning("VALS ------------------------ " + str(vals['formula_id']))
            param_vals = self._set_volume_param(vals['formula_id'])
            vals.update(param_vals)
            _logger.warning("PARAMS ------------------------ " + str(param_vals))
            _logger.warning("VALSSSSSSSSSSSS ------------------------ " + str(vals))
            
            return super(Location, self).create(vals)

    @api.onchange('formula_id')
    def _set_volume_param_onchange(self):

        _logger.warning("Changed Formula ------------------------- " + str(self.formula_id.name))

        length = False
        breadth = False
        height = False
        diameter = False
        
        formula_format = self.formula_id.formula
        if formula_format:
            if "length" in formula_format: length = True
            if "breadth" in formula_format: breadth = True
            if "height" in formula_format: height = True
            if "diameter" in formula_format: diameter = True
        
        self.is_length = length
        self.is_breadth = breadth
        self.is_height = height
        self.is_diameter = diameter
        
        _logger.warning("Length ------------------------- " + str(self.is_length))
        _logger.warning("Breadth ------------------------- " + str(self.is_breadth))
        _logger.warning("Height ------------------------- " + str(self.is_height))
        _logger.warning("Diameter ------------------------- " + str(self.is_diameter))
