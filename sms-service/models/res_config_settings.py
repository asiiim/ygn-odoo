# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sms_token = fields.Char(string='Points per currency', help="Token generated from SMS website.")
    sms_sender = fields.Char(string='Points Rounding', help="It should be the identity provided to you by SMS")
    sms_url = fields.Char(string='SMS API URL', help="The URL to send the request")
    sms_credit_url = fields.Char(string='SMS CREDIT API URL', help="The URL to send the credit request")

    def get_sms_credentials(self):
        params = self.env['ir.config_parameter'].sudo()
        return dict(
            sms_token=params.get_param('sms_token', default=''),
            sms_sender=params.get_param('sms_sender', default=''),
            sms_url=params.get_param('sms_url', default=''),
            sms_credit_url=params.get_param('sms_credit_url', default=''),
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
        params.set_param('sms_token', self[0].sms_token or '')
        params.set_param('sms_sender', self[0].sms_sender or '')
        params.set_param('sms_url', self[0].sms_url or '')
        params.set_param('sms_credit_url', self[0].sms_credit_url or '')
