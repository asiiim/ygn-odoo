# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

from pyparsing import (Literal, CaselessLiteral, Word, Combine, Group, Optional,
                       ZeroOrMore, Forward, nums, alphas, oneOf)
import math
import operator

import logging

_logger = logging.getLogger(__name__)

STORAGE_PARAM = ('length', 'breadth', 'height', 'radius', 'pi')

class StorageParameter(models.Model):
    _name = 'storage.parameter'

    name = fields.Char("Name")

    length = fields.Float(string="Length (in meter)", help="Length of the Storage.", default=0.0)
    breadth = fields.Float(string="Breadth (in meter)", help="Breadth of the Storage.", default=0.0)
    height = fields.Float(string="Height (in meter)", help="Height of the Storage.", default=0.0)
    radius = fields.Float(string="Radius (in meter)", help="Radius or Input the Half of the Diameter Value.", default=0.0)
    pi = fields.Float(string="PI", default=3.142857142857143)

    formula_id = fields.Many2one('storage.logic', string="Formula")
    volume = fields.Float(compute="_calc_volume", string="Volume (in Kilolitre)", help="Volume of the Storage", store=True)

    @api.model
    def _param_fields(self):
        """Returns the list of param fields."""
        return list(STORAGE_PARAM)

    @api.multi
    @api.depends('formula_id')
    def _calc_volume(self):

        '''
        The purpose of this function is to calculate the volume of the storage.

        :param address: browse record of the storage.logic for the formula and parameter
        :returns: volume of the storage
        :rtype: float
        '''
        # get the information that will be injected into the volume calculation
        # get the formula
        formula_format = self.formula_id.formula
        if formula_format:
            args = {
                'length': self.length or 0.0,
                'breadth': self.breadth or 0.0,
                'height': self.height or 0.0,
                'radius': self.radius or 0.0,
                'pi': self.pi or 0.0,
            }

            for field in self._param_fields():
                if field:
                    args[field] = getattr(self, field) or ''
            
            try:
                result = eval(str(formula_format % args))
                for rec in self:
                    rec.volume = result
                return result
            except:
                _logger.info(_("Please provide parameter value greater than 0.0"))


