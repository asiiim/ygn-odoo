# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, http, _
import json
import logging
import requests
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SMSMultiple(models.Model):
    _name = 'sms.multiple'

    name = fields.Char(string="Name")
    sms_messaging_list_ids = fields.Many2many('sms.messaging.list', 'group_multi_sms_rel', 'sms_messaging_list_ids', 'sms_multiple_id', string="SMS Groups")
    receivers = fields.Text(string="To",compute="_compute_receivers", help="Comma Separated 10-digit mobile numbers.", store=True)
    failed_receivers = fields.Char(string="Failed Names", store=True)
    text = fields.Text(string="Text", help="SMS to be sent.")
    total_partners_count = fields.Integer(string="Total Partners Count", default=0)
    failed_partners_count = fields.Integer(string="Failed Partners Count", default=0)
    credits_consumed_count = fields.Integer(string="Credits Consumed in SMS", default=0)
    message_id = fields.Integer(string="Message ID",  default=0)
    is_button_pressed = fields.Boolean(string="Is button pressed?", default=False)
    is_sent = fields.Boolean(string="Sent?")


    @api.multi
    def _compute_receivers(self):
        for record in self:
            record.write({
                'receivers': ""
            })
            record.write({
                'failed_receivers': ""
            })
            partner_sudo = record.env['res.partner'].sudo()
            if record.sms_messaging_list_ids:
                for sms_messaging_list_id in record.sms_messaging_list_ids:
                    if sms_messaging_list_id.partner_ids:
                        for partner_id in sms_messaging_list_id.partner_ids:
                            partner = partner_sudo.search([('id','=',partner_id.id)])
                            if partner.mobile:
                                record.write({
                                    'receivers': record.receivers + str(partner.mobile)+',',
                                    'total_partners_count': record.total_partners_count + 1
                                })
                            else:
                                record.write({
                                    'failed_receivers': record.failed_receivers + str(partner.name) + ',',
                                    'failed_partners_count': record.failed_partners_count + 1
                                })
            if record.receivers:
                record.write({
                    'receivers': record.receivers[:-1]
                })
            if record.failed_receivers:
                record.write({
                    'failed_receivers': record.failed_receivers[:-1]
                })

    @api.multi
    def sendSms(self):
        for record in self:
            if not record.is_button_pressed:
                record._compute_receivers()
                try:
                    result = requests.post(record.env['ir.config_parameter'].sudo().get_param('sms_url'), params={'auth_token': record.env['ir.config_parameter'].sudo().get_param('sms_token'), 'from': record.env['ir.config_parameter'].sudo().get_param('sms_sender'), 'to': record.receivers,'text': record.text}).json()
                except Exception as e:
                    raise UserError(_(
                        'Cannot contact SMS servers. \nPlease make sure that your Internet connection is up and running (%s).') % e)
                if result:
                    _logger.warning(str(result))
                    if result['response_code'] == 200:
                        record.write({
                            'is_button_pressed': True,
                            'is_sent': True,
                            'credits_consumed_count': result['credit_consumed'],
                            'message_id': result['message_id']
                        })
                    else:
                        raise UserError(_('An Error Occured: '+ str(result['response'])))
                else:
                    raise UserError(_("An Error Occured"))
