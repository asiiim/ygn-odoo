# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import Response
from odoo.http import request
from operator import itemgetter

import logging
_logger = logging.getLogger(__name__)


class InvoiceController(http.Controller):

    @http.route('/api/invoice/create', type='json', auth='public', methods=['POST'], csrf=False)
    def create_invoice(self, db, username, password, customer_id, sales_reference, invoice_lines, **args):
        
        # Login in:
        try:
            request.session.authenticate(db, username, password)
        except Exception as e:
            # Invalid database:
            info = "Login Error {}".format((e))
            error = "invalid_login"
            _logger.error(info)
            return {
                'info': info,
                'error': error
            }

        uid = request.session.uid
        # Login failed:
        if not uid:
            info = "Authorization Failed"
            error = "authorization_failed"
            _logger.error(info)
            return {
                'status': 401,
                'info': info,
                'error': error
            }

        # Model Env
        partner = request.env['res.partner']
        invoice = request.env['account.invoice']
        invoice_line = request.env['account.invoice.line']
        account_env = request.env['account.account']
        tax_env = request.env['account.tax']
        
        inv_lines = []

        customer = partner.search([('id', '=', customer_id)])
        if not customer:
            return {
                "status": 500,
                "message": "You need a customer for the invoice in the system, please create it first.",
            }   
        else:
            vals = {
                'partner_id': customer_id,
                'name': sales_reference
            }
            inv_rec = invoice.create(vals)

            # invoice lines creation
            for invl in invoice_lines:
                account = account_env.search([('name', '=', invl['account_name'])])
                tax = tax_env.search([('name', '=', invl['tax']), ('type_tax_use', '=', "sale")], limit=1)

                if not account:
                    return {
                        "status": 500,
                        "message": "Please provide account for the given invoice line.",
                    }
                else:
                    if not tax:
                        inv_line_vals = {
                            'name': invl['name'],
                            'quantity': invl['quantity'],
                            'price_unit': invl['price_unit'],
                            'account_id': account.id,
                            'invoice_id': inv_rec.id
                        }
                    else:
                        inv_line_vals = {
                            'name': invl['name'],
                            'quantity': invl['quantity'],
                            'price_unit': invl['price_unit'],
                            'account_id': account.id,
                            'invoice_id': inv_rec.id,
                            'invoice_line_tax_ids': [(4, tax.id)]
                        }
                inv_line_id = invoice_line.create(inv_line_vals)
                inv_lines.append(inv_line_id.id)

                # compute tax
                inv_rec.compute_taxes()

                # validate the invoice
                inv_rec.action_invoice_open()

            return {
                "status": 202,
                "message": "Invoice created successfully...",
                "invoice_id": inv_rec.id,
                "invoice_lines": inv_lines
            }
