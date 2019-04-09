# -*- coding: utf-8 -*-

from odoo import models, fields, api

class DipTestWizard(models.TransientModel):
    """ A wizard to take the dip value to calulate the filled volume in the storage. """
    _name = "station.diptest.wizard"
    _inherit = "stock.location"
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
        })
        return {'type': 'ir.actions.act_window_close'}
