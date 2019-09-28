# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ygen_username = fields.Char(string='Username', help="Username of the database you are trying to access.")
    ygen_password = fields.Char(string='Password', help="Password of the required username.")
    ygen_url = fields.Text(string='Base URL', help="Server API Base URL.")
    ygen_db = fields.Char(string='Database Name', help="Server Database Name.")

    def get_credentials(self):
        params = self.env['ir.config_parameter'].sudo()
        return dict(
            ygen_username=params.get_param('ygen_username', default=''),
            ygen_password=params.get_param('ygen_password', default=''),
            ygen_url=params.get_param('ygen_url', default=''),
            ygen_db=params.get_param('ygen_db', default=''),
        )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(self.get_credentials())
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('ygen_username', self[0].ygen_username or '')
        params.set_param('ygen_password', self[0].ygen_password or '')
        params.set_param('ygen_url', self[0].ygen_url or '')
        params.set_param('ygen_db', self[0].ygen_db or '')
