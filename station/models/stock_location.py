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
    volume = fields.Float(compute="_calc_volume", string="Volume (in Kilolitre)", help="Volume of the Storage.", store=True)

    @api.model
    def _param_fields(self):
        """Returns the list of param fields."""
        return list(STORAGE_PARAM)

    @api.multi
    @api.depends('formula_id')
    def _calc_volume(self):

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
    product_ids = fields.Many2many('product.template', 'stock_station_product', 'station_id', 'product_id', 'Products')
    product_quantity = fields.Float(related="quant_ids.quantity", string="On Hand")
    dip = fields.Float(string="Dip Value (in meter)", help="Value of the Dip Test.", default=0.0)
    is_dip = fields.Boolean(default=False)
    filled_volume = fields.Float(compute="_calc_filled_volume", string="Remaining Volume (in Kilolitre)", help="Remaining 'Volume in the storage.", store=True)

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
                    self._make_inv_adjustment(on_hand)
                except:
                    _logger.info(_("Please provide parameter value greater than 0.0"))
                    # raise UserError(_("Please provide parameter value greater than 0.0"))

    def _make_inv_adjustment(self, qty):
        _logger.warning("Adjustment -------------------------- " + str(qty))

    def _get_action(self, action_xmlid):
        action = self.env.ref(action_xmlid).read()[0]
        if self:
            action['dip'] = self.dip
        return action

    def get_diptest_wizard_action(self):
        return self._get_action('station.diptest_wizard_action')
