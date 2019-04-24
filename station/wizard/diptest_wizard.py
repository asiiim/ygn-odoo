# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class DipTestWizard(models.TransientModel):
    """ A wizard to take the dip value to calulate the filled volume in the storage. """
    _name = "station.diptest.wizard"
    _description = "Oil Station Tank Diptest Wizard"

    name = fields.Char(string="Remarks")

    dip = fields.Float(string="Dip Value", default=0.0)

    def _default_station(self):
        return self.env['stock.location'].browse(self._context.get('active_id'))

    station_id = fields.Many2one('stock.location', default=_default_station)


    @api.multi
    def apply_dip_value(self):
        self.station_id.write({
            'dip': self.dip,
            'is_dip': True,
        })
        self.station_id._calc_filled_volume()
        return {'type': 'ir.actions.act_window_close'}
