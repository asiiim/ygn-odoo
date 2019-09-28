# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, http, _
import json
import logging
import requests
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    remote_id = fields.Integer("Remote ID", help="This is the remote id of the record which has been generated from another database server.", readonly=True, copy=False)
    # remote_invoice_number = fields.Char("Remote Invoice Number", help="This is the remote invoice number of the record which has been generated from another database server.", readonly=True, copy=False)

    @api.multi
    def inv_synchronization(self, partner_id, sale_ref, invoice_lines):
        for record in self:
            headers = {'Content-Type': 'application/json'}
            url = record.env['ir.config_parameter'].sudo().get_param('ygen_url') + 'invoice/create'
            params = {
                "params": {
                    "db": record.env['ir.config_parameter'].sudo().get_param('ygen_db'),
                    "username": record.env['ir.config_parameter'].sudo().get_param('ygen_username'),
                    "password": record.env['ir.config_parameter'].sudo().get_param('ygen_password'),
                    "customer_id": partner_id,
                    "sales_reference": sale_ref,
                    "invoice_lines": invoice_lines
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
                    remote_id = response['result'].get('invoice_id')
                    # invoice_number = response['result'].get('invoice_number')
                    return remote_id
                else:
                    raise UserError(_('An Error Occured: '+ str(response['result'].get('message'))))
            else:
                raise UserError(_("An Error Occured"))

    @api.multi
    def invoice_validate(self):
        validate = super(AccountInvoice, self).invoice_validate()

        # account env
        account_env = self.env['account.account']

        # tax env
        tax_env = self.env['account.tax']
        
        # invoice line env
        invoice_lines = []
        for invoice_line in self.invoice_line_ids:
            taxline_arr = []
            
            for tax in invoice_line.invoice_line_tax_ids:
                taxline_arr.append(tax.name)

            invoice_lines.append({
                'name': invoice_line.name,
                'quantity': invoice_line.quantity,
                'price_unit': invoice_line.price_unit,
                'account_name': account_env.search([('name', '=', invoice_line.account_id.name)]).name,
                'tax': tax_env.search([('name', '=', taxline_arr[0]), ('type_tax_use', '=', "sale")], limit=1).name,
                'discount': invoice_line.discount
            })

        remote_id = self.inv_synchronization(self.partner_id.remote_id, self.name, invoice_lines)
        self.write({
            'remote_id': remote_id  
        })

        return validate

   