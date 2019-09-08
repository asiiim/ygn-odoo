# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, http, _
import json
import logging
import requests
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class SMSCredit(models.Model):
    _name = 'sms.credit'

    name = fields.Char(string="Credit Available", readonly=True, track_visibility='onchange')

    @api.multi
    def requestSmsCredit(self):
        for record in self:
            try:
                result = requests.post(
                    record.env['ir.config_parameter'].sudo().get_param('sms_url') + 'credit', 
                    data={
                        'auth_token': record.env['ir.config_parameter'].sudo().get_param('sms_token')}
                    ).json()
            except Exception as e:
                raise UserError(_(
                    'Cannot contact SMS servers. \nPlease make sure that your Internet connection is up and running (%s).') % e)
            if result:
                if result['response_code'] == 202:
                    record.write({
                        'name': result['available_credit']
                    })
                else:
                    raise UserError(_('An Error Occured'))
            else:
                raise UserError(_("An Error Occured"))
