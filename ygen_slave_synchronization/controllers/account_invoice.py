# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import Response
from odoo.http import request
from operator import itemgetter
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.exceptions import UserError, AccessError

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
                'code': 401,
                'info': info,
                'error': error
            }

        # Model Env
        partner = request.env['res.partner']
        invoice_env = request.env['account.invoice']
        invoice_line = request.env['account.invoice.line']
        account_env = request.env['account.account']
        tax_env = request.env['account.tax']
        
        # arrays
        inv_lines = []

        customer = partner.search([('id', '=', customer_id)])
        if not customer:
            return {
                "code": 500,
                "message": "You need a customer for the invoice in the system, please create it first.",
            }   
        else:
            # invoice dict
            company_id = request.env.user.company_id.id
            journal_id = (invoice_env.with_context(company_id=company_id).default_get(['journal_id'])['journal_id'])
            if not journal_id:
                raise UserError(_('Please define an accounting sales journal for this company.'))
            invoice_vals = {
                'name': sales_reference or '',
                'origin': sales_reference or '',
                'type': 'out_invoice',
                'account_id': account_env.search([('user_type_id', '=', request.env.ref('account.data_account_type_revenue').id)], limit=1).id,
                'partner_id': customer_id,
                'journal_id': journal_id,
                'fiscal_position_id': '',
                'company_id': company_id,
                'state': 'draft'
            }
            
            # create invoice
            inv_rec = invoice_env.create(invoice_vals)

            # invoice lines creation
            for invl in invoice_lines:
                account = account_env.search([('name', '=', invl['account_name'])])
                tax = tax_env.search([('name', 'in', invl['tax']), ('type_tax_use', '=', "sale")])

                if not account:
                    return {
                        "code": 500,
                        "message": "Please provide account for the given invoice line.",
                    }
                else:
                    inv_line_vals = {
                        'name': invl['name'],
                        'quantity': invl['quantity'],
                        'price_unit': invl['price_unit'],
                        'account_id': account.id,
                        'invoice_id': inv_rec.id,
                        'invoice_line_tax_ids': [(6, 0, tax.ids)] if tax else "",
                        'discount': invl['discount'],
                        'origin': sales_reference or '',
                    }
                
                inv_line_id = invoice_line.create(inv_line_vals)
                inv_lines.append(inv_line_id.id)

                # compute tax
                inv_rec.compute_taxes()

                # validate invoice
                # _logger.warning("Invoice State :::::: " + str(inv_rec.state))
                # if inv_rec.state != 'draft':
                #     return {
                #         "code": 500,
                #         "message": "Selected invoice(s) cannot be validated as they are not in 'Draft' state in the slave server.",
                #     }
                # inv_rec.action_invoice_open()

            return {
                "code": 200,
                "message": "Invoice created successfully...",
                "invoice_id": inv_rec.id,
                "invoice_lines": inv_lines
            }
