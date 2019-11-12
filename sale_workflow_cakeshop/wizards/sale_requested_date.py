# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, api, _
from odoo.exceptions import Warning, ValidationError, UserError

import logging

_logger = logging.getLogger(__name__)


class SaleRequestedDate(models.TransientModel):
    _name = 'sale.requested.date'

    requested_date = fields.Datetime(string="New Delivery Date")

    @api.multi
    def change_requested_date(self):

        so_obj = self.env['sale.order']
        so = so_obj.browse(self._context.get('active_id'))

        stock_pickings = self.env['stock.picking'].search([('origin', '=', so.name), ('state', '!=', 'cancel')])
        
        for stkpk in stock_pickings:
            if stkpk.state in ['confirmed', 'assigned']:
                stkpk.write({'scheduled_date': self.requested_date})

        so.write({'requested_date': self.requested_date})
