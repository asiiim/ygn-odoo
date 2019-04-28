# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class QuickSaleWizard(models.TransientModel):
    """ A wizard to take the quantity of the product to sell with current station
    and current product. """
    _name = "station.quick_sale.wizard"
    _description = "Quick Product Sale Wizard"

    quantity = fields.Float(string="Quantity (in Liter)", default=0.0)

    def _default_station(self):
        return self.env['stock.location'].browse(self._context.get('active_id'))

    station_id = fields.Many2one('stock.location', default=_default_station)

    @api.multi
    def apply_qty_value(self):
        self.station_id.write({
            'sold_qty': self.quantity,
        })
        self.station_id.confirm_quick_sale()
        return {'type': 'ir.actions.act_window_close'}
