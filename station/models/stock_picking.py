# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)

class Picking(models.Model):
    _inherit = "stock.picking"
    
    @api.model
    def create(self, vals):

        src_loc = self.env['stock.location'].search([('id', '=', vals['location_id'])])
        dest_loc = self.env['stock.location'].search([('id', '=', vals['location_dest_id'])])

        if src_loc.is_product_filter and dest_loc.is_product_filter:
            if src_loc.product_id != dest_loc.product_id:
                raise UserError(_('Source and Destination locations have different products.\n Please select the locations with same product.'))
            
            if len(vals['move_lines']) > 1:
                raise UserError(_('Please keep only one product in the move line.'))
            
            if vals.get('move_lines'):
                for moveline in vals['move_lines']:
                    for move in range(len(moveline)):
                        if move == 2:
                            _logger.warning("Product in create ----- " + str(moveline[move]['product_id']))
                            if moveline[move]['product_id'] != src_loc.product_id.id:
                                raise UserError(_('Product doesnot match. Product must match with  that of the source and destination locations for the transfer operation.'))


        res = super(Picking, self).create(vals)
        return res

    @api.multi
    def write(self, vals):

        if self.location_id.is_product_filter and self.location_dest_id.is_product_filter:
            if vals.get('move_lines'):
                if len(vals['move_lines']) > 1:
                    raise UserError(_('Products to be tansferred cannot be changed now.\nPlease click on DISCARD button and click on CREATE button to create new stock operation for the product transfer.'))
                
        res = super(Picking, self).write(vals)
        return res