# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from collections import namedtuple
import json
import time

from itertools import groupby
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from operator import itemgetter

import logging

_logger = logging.getLogger(__name__)

class Picking(models.Model):
    _inherit = "stock.picking"
    
    @api.model
    def create(self, vals):
        _logger.warning("Picking Vals ------------------ " + str(vals))

        _logger.warning("Picking Vals In IF ------------------ " + str(vals['location_id']))
        _logger.warning("Picking Vals In IF ------------------ " + str(vals['location_dest_id']))

        src_loc = self.env['stock.location'].search([('id', '=', vals['location_id'])])
        dest_loc = self.env['stock.location'].search([('id', '=', vals['location_dest_id'])])

        _logger.warning("Picking Products ------------------ " + str(src_loc.product_id))
        _logger.warning("Picking Products ------------------ " + str(dest_loc.product_id))

        _logger.warning("Filter Products ------------------ " + str(src_loc.is_product_filter))
        _logger.warning("Filter Products ------------------ " + str(dest_loc.is_product_filter))

        if src_loc.is_product_filter and dest_loc.is_product_filter:
            if src_loc.product_id != dest_loc.product_id:
                raise UserError(_('Source and Destination locations have different products.\n Please select the locations with same product.'))
            
            if len(vals['move_lines']) > 1:
                raise UserError(_('Please keep only one product in the move line.'))
            _logger.warning("Moving Products --------- " + str(len(vals['move_lines'])))
            
        res = super(Picking, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        _logger.warning("Write SELF---------- " + str(self.name))

        if self.location_id.is_product_filter and self.location_dest_id.is_product_filter:
            
            # NEED TO WORK HERE --------------------------------------------------------

            if vals.get('move_lines'):
                _logger.warning("Vals get move lines -------- ")
                if len(vals['move_lines']) > 1:
                    _logger.warning("Total Move Lines Vals -------- " + str(len(vals['move_lines'])))

                    raise UserError(_('Please keep only one product in the move line.'))

            # ---------------------------------------------------------------------------

        res = super(Picking, self).write(vals)
        
        return res