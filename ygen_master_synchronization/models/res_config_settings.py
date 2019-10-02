# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

import json
import logging
import requests
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ygen_username = fields.Char(string='Username', help="Username of the database you are trying to access.")
    ygen_password = fields.Char(string='Password', help="Password of the required username.")
    ygen_url = fields.Text(string='Base URL', help="Server API Base URL.\n Basically, end the url with /api/")
    ygen_db = fields.Char(string='Database Name', help="Server Database Name.")
    ok_tested = fields.Char(string="Verified", readonly=True, copy=False, default=False)

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

    @api.multi
    def test_connection(self):
        for record in self:
            headers = {'Content-Type': 'application/json'}
            url = record.env['ir.config_parameter'].sudo().get_param('ygen_url') + 'test'
            params = {
                "params": {
                    "db": record.ygen_db,
                    "username": record.ygen_username,
                    "password": record.ygen_password
                }
            }
            json_params = json.dumps(params)

            try:
                response = requests.post(url, data=json_params, headers=headers).json()

            except Exception as e:
                raise UserError(_(
                    'Could not connect to server. \n(%s)') % e)
            if response:
                if response['result'].get('code') == 200:
                    record.ok_tested = True
                else:
                    raise UserError(_('An Error Occured: '+ str(response['result'].get('message'))))
            else:
                raise UserError(_("An Error Occured"))