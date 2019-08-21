# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, http, _
import json
import logging
import requests
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SMSSingle(models.Model):
    _name = 'sms.single'

    name = fields.Char(string="Name")
    receiver = fields.Text(string="To", help="Comma Separated 10-digit mobile numbers.")
    text = fields.Text(string="Text", help="SMS Message to be sent.")
    is_sent = fields.Boolean(string="SMS Sent?")

    @api.multi
    def sendSms(self):
        for record in self:
            try:
                result = requests.post(record.env['ir.config_parameter'].sudo().get_param('sms_url'), data={'auth_token': record.env['ir.config_parameter'].sudo().get_param('sms_token'), 'from': record.env['ir.config_parameter'].sudo().get_param('sms_sender'), 'to': record.receiver,'text': record.text}).json()
            except Exception as e:
                raise UserError(_(
                    'Cannot contact SMS servers. \nPlease make sure that your Internet connection is up and running (%s).') % e)
            if result:
                if result['response_code'] == 200:
                    record.write({
                    'is_sent': True
                    })
                else:
                    raise UserError(_('An Error Occured: '+ str(result['response'])))
            else:
                raise UserError(_("An Error Occured"))
