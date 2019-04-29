# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
import datetime
import logging

_logger = logging.getLogger(__name__)


class DiptestLog(models.Model):
    _name = "station.diptest_log"

    name = fields.Char(compute='compute_diptest_log_name', string='Log', readonly=True, store=True)
    dip_value = fields.Char(string='Dip Value')
    station_id = fields.Many2one('stock.location', string="Station")
    filled_volume = fields.Float(related='station_id.filled_volume')
    test_by = fields.Many2one('res.users', default='default_user', readonly=True)
    test_date = fields.Datetime('Test Date')

    def compute_diptest_log_name(self):
        for log in self:
            date = datetime.datetime.strptime(log.test_date, '%Y-%m-%d %H:%M:%S')
            log.name = str(log.id) + '/' + str(log.station_id.name) + '/' + str(date.strftime("%Y/%m/%d"))

    def default_user(self):
        return self.env['res.users'].browse(self._context.get('active_id'))
