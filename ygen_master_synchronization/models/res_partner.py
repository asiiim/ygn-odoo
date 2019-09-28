# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, http, _
import json
import logging
import requests
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    remote_id = fields.Integer("Remote ID", help="This is the remote id of the record which has been generated from another database server.", readonly=True, copy=False)

    @api.multi
    def partner_synchronization(self, name, mobile, phone, tin):
        for record in self:

            headers = {'Content-Type': 'application/json'}
            url = record.env['ir.config_parameter'].sudo().get_param('ygen_url') + 'invoice/customer'
            params = {
                "params": {
                    "db": record.env['ir.config_parameter'].sudo().get_param('ygen_db'),
                    "username": record.env['ir.config_parameter'].sudo().get_param('ygen_username'),
                    "password": record.env['ir.config_parameter'].sudo().get_param('ygen_password'),
                    "name": name,
                    "mobile": mobile,
                    "phone": phone,
                    "tin": tin
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
                    remote_id = response['result'].get('id')
                    return remote_id
                else:
                    raise UserError(_('An Error Occured: '+ str(response['result'].get('message'))))
            else:
                raise UserError(_("An Error Occured"))

    @api.model
    def create(self, values):
        partner = super(ResPartner, self).create(values)
        remote_id = partner.partner_synchronization(partner.name or "", partner.mobile or "", partner.phone or "", partner.vat or "")
        partner.write({'remote_id': remote_id})
        return partner
