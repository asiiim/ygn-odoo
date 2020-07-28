# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, http, _
import json
import logging
import requests
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SMSSingle(models.Model):
    _name = 'ygen.sms.single'

    reference = fields.Char(string="Reference", required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'), track_visibility='onchange')
    @api.model
    def create(self, vals):
        vals['reference'] = self.env['ir.sequence'].next_by_code('ygen.sms.single') or _('New')
        result = super(SMSSingle, self).create(vals)
        return result
    
    @api.multi
    def name_get(self):
        return [(value.id, "%s" % (value.reference)) for value in self]

    name = fields.Char(string="Name", track_visibility='onchange', copy=False)
    receiver = fields.Text(string="To", help="Comma Separated 10-digit mobile numbers.", track_visibility='onchange')
    text = fields.Text(string="Text", help="SMS Message to be sent.", track_visibility='onchange')
    is_sent = fields.Boolean(string="SMS Sent?", default=False, store=True, track_visibility='onchange', copy=False)
    sms_credits_consumed = fields.Integer(string="Credits consumed", store=True, track_visibility='onchange', copy=False)
    remaining_credits = fields.Char('Remaining Credit')
    partner_id = fields.Many2one('res.partner', string="Recipient")

    @api.onchange('partner_id')
    def onchange_partner(self):
        for rec in self:
            if rec.partner_id:
                rec.receiver = rec.partner_id.mobile

    @api.multi
    def send_sms(self):
        for record in self:
            try:
                result = requests.post(
                    record.env['ir.config_parameter'].sudo().get_param('ygen_sms_url') + 'send', 
                    data={
                        'auth_token': record.env['ir.config_parameter'].sudo().get_param('ygen_sms_token'), 
                        'from': record.env['ir.config_parameter'].sudo().get_param('ygen_sms_sender'), 
                        'to': record.receiver, 
                        'text': record.text}).json()
            except Exception as e:
                raise UserError(_(
                    'Cannot contact SMS servers. \nPlease make sure that your Internet connection is up and running (%s).') % e)
            if result:
                if not result['error']:
                    credit = 0
                    for data in result['data']['valid']:
                        credit += data['credit']
                    record.write({
                        'is_sent': True,
                        'sms_credits_consumed': credit
                    })
                else:
                    raise UserError(_('An Error Occured: '+ str(result['message'])))
            else:
                raise UserError(_("An Error Occured"))
