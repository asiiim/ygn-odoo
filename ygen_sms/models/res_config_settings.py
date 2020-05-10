# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ygen_sms_token = fields.Char(string='Token', help="Token generated from SMS website.")
    ygen_sms_sender = fields.Char(string='Sender', help="It should be the identity provided to you by SMS")
    ygen_sms_url = fields.Char(string='Base URL', help="The URL to send the request")
    ygen_sms_credit_url = fields.Char(string='SMS Credit URL', help="The URL to request SMS Credit")

    def get_sms_credentials(self):
        params = self.env['ir.config_parameter'].sudo()
        return dict(
            ygen_sms_token=params.get_param('ygen_sms_token', default=''),
            ygen_sms_sender=params.get_param('ygen_sms_sender', default=''),
            ygen_sms_url=params.get_param('ygen_sms_url', default=''),
            ygen_sms_credit_url=params.get_param('ygen_sms_credit_url', default=''),
        )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(self.get_sms_credentials())
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('ygen_sms_token', self[0].ygen_sms_token or '')
        params.set_param('ygen_sms_sender', self[0].ygen_sms_sender or '')
        params.set_param('ygen_sms_url', self[0].ygen_sms_url or '')
        params.set_param('ygen_sms_credit_url', self[0].ygen_sms_credit_url or '')
