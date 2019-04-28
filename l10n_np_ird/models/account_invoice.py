# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

import datetime
import logging
import json
import threading

import requests

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError
from odoo import tools

_logger = logging.getLogger(__name__)

TIMEOUT = 20

ird_api_codes = {
    104: "Model invalid",
    200: "Success",
    102: "Exception while saving bill details , Please check model fields and values",
    101: "Bill already exists",
    100: "API credentials do not match",
    103: "Unknown exceptions, Please check API URL and model fields and values"
}


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    sent_to_ird = fields.Boolean(string='Sent To IRD', readonly=True, default=False, copy=False,
        track_visibility='onchange', help="It indicates that the invoice has been sent to IRD.") 
    is_ird_realtime = fields.Boolean(string='Is Realtime', readonly=True, default=False, copy=False,
        track_visibility='onchange', help="It indicates whether the invoice sent to IRD is in realtime.")

    # Override
    @api.multi
    def action_invoice_open(self):
        open_invoices = super(AccountInvoice, self).action_invoice_open()
        # send invoice to IRD
        self.process_ird_invoices_queue(self.ids)
        return open_invoices

    @api.model
    def process_ird_invoices_queue(self, ids=None, limit=1000):
        """ Send immediately queued invoices, committing after each
            invoice is sent - this is not transactional and should
            not be called during another transaction!

            :param list ids: optional list of invoices ids to send. If passed
                no search is performed, and these ids are used
                instead.
            :param dict context: if a 'filters' key is present in context,
                this value will be used as an additional
                filter to further restrict the open or 
                paid invoices to send (by default all 'open' 
                or paid invoices are sent).
        """
        filters = ['&',
                    '&',
                    ('type', 'in', ['out_invoice','out_refund']),
                    ('state', 'in', ['open','paid']),
                    ('sent_to_ird', '=', False)
                ]
        if 'filters' in self._context:
            filters.extend(self._context['filters'])
        filtered_ids = self.search(filters, limit=limit).ids
        if not ids:
            ids = filtered_ids
        else:
            ids = list(set(filtered_ids) & set(ids))
        ids.sort(reverse=True)
        
        res = None
        try:
            # auto-commit except in testing mode
            auto_commit = not getattr(threading.currentThread(), 'testing', False)
            res = self.browse(ids)._send_to_ird(auto_commit=auto_commit)
        except Exception:
            _logger.exception("Failed processing invoice queue")
        return res
    
    @api.multi
    def _process_prepare_taxes(self):
        self.ensure_one()
        taxes = {key:{'amount': 0.0,'base': 0.0} for key in ['vat', 'hst', 'esf', 'excise']}
        # Assign ammount and base for respective tax group
        for amount_by_group in self._get_tax_amount_by_group():
            taxes[amount_by_group[0].lower()] = {'amount': amount_by_group[1],'base': amount_by_group[2]}

        return taxes

    @api.multi
    def _prepare_payload_for_ird(self, ird_api_url):
        self.ensure_one()
        # Get ird api credentials of current company
        username = self.company_id.keychain_id.login
        password = self.company_id.keychain_id._get_password()
        
        # Build request url
        request_url_suffix = None
        if self.type == "out_invoice":
            request_url_suffix = "api/bill"
        else:
            request_url_suffix = "api/billreturn"
        request_api_bill_url = "%s%s" % (ird_api_url, request_url_suffix)
        
        # Calculate fiscal year
        fy_date_range = self.company_id.compute_fiscalyear_dates(fields.Date().from_string(self.date_invoice))
        fiscal_year = str(fy_date_range['date_from'].year) + "." + str(fy_date_range['date_to'].year)
        
        # Process and calculate for tax groups
        tax_group_amounts = self._process_prepare_taxes()
        is_realtime = True if (datetime.datetime.now() - fields.Datetime().from_string(self.write_date)) < datetime.timedelta(minutes=10) else False
        data = {
            "username": username,
            "password": password,
            "seller_pan": self.company_id.vat,
            "buyer_pan": self.partner_id.vat if self.partner_id and self.partner_id.vat else "",
            "buyer_name": self.partner_id.name if self.partner_id else "",
            "fiscal_year": fiscal_year,
            "total_sales": self.amount_total,
            "taxable_sales_vat": tax_group_amounts["vat"]["base"],
            "vat": tax_group_amounts["vat"]["amount"],
            "excisable_amount":tax_group_amounts["excise"]["base"],
            "excise":tax_group_amounts["excise"]["amount"],
            "taxable_sales_hst":tax_group_amounts["hst"]["base"],
            "hst":tax_group_amounts["hst"]["amount"],
            "amount_for_esf":tax_group_amounts["esf"]["base"],
            "esf":tax_group_amounts["esf"]["amount"],
            "export_sales":self.amount_export,
            "tax_exempted_sales":self.amount_non_taxable,
            "isrealtime": is_realtime,
            "datetimeclient": fields.Datetime().now()
        }
        if self.type == "out_invoice":
            # make payload for invoice post
            data.update({
                "invoice_number": self.number,
                "invoice_date": fields.Date().from_string(self.date_invoice).strftime("%Y.%m.%d")
            })
        elif self.type == "out_refund":
            # make payload for invoice post
            data.update({
                "ref_invoice_number": self.refund_invoice_id.number,
                "credit_note_number": self.number,
                "credit_note_date": fields.Date().from_string(self.date_invoice).strftime("%Y.%m.%d"),
                "reason_for_return": self.name,
            })
        return data, request_api_bill_url

    def _sanitize_data_for_chatter(self, data):
        sanitized_data = data.copy()
        del sanitized_data["username"]
        del sanitized_data["password"]
        msg = "Data sent to IRD: <br/>"
        for k,v in sanitized_data.items():
            msg += "%s: %s<br/>" % (k,v)
        return msg

    @api.multi
    def _send_to_ird(self, auto_commit=False, raise_exception=False):
        """ Sends the selected open/paid and unsent invoices immediately.
            Invoices successfully submitted are marked as 'sent_to_ird', and those
            that fail to be deliver are sent later, and the corresponding error 
            invoice is output in the server logs.

            :param bool auto_commit: whether to force a commit of the invoice status
                after sending each invoice (meant only for scheduler processing);
                should never be True during normal transactions (default: False)
            :param bool raise_exception: whether to raise an exception if the
                invoice sending process has failed
            :return: True
        """
        # Get api url
        ird_api_url = self.env['ir.config_parameter'].sudo().get_param('ird_api_uri')
        ird_api_url = ird_api_url if ird_api_url.endswith("/") else ird_api_url + "/"
        
        # Build headers
        headers = {"Content-type": "application/json"}
        for invoice in self:
            try:
                if invoice.state in ['open','paid'] and not invoice.sent_to_ird:
                    # Check is it realtime
                    # prepare payload
                    data, request_api_bill_url = invoice._prepare_payload_for_ird(ird_api_url)
                    try:
                        res = requests.post(request_api_bill_url, data=json.dumps(data), headers=headers, timeout=TIMEOUT)
                        res.raise_for_status()
                        content = res.text
                        if int(content) == 200:
                            # Make copy of data to sanitize for 
                            # logging note in the chatter
                            sanitized_data = invoice._sanitize_data_for_chatter(data)
                            # Find whether it is Invoice or Credit note
                            invoice_type = "Invoice" if invoice.type == "out_invoice" else "Credit Note"
                            msg = _("%s sent to the IRD with %s number %s<br/><br/>%s") % (invoice_type, invoice_type, invoice.number, str(sanitized_data))
                            invoice.message_post(
                                body=msg,
                                subject="Invoice sent to IRD"
                            )
                            _logger.info(msg.replace("<br/>",", "))
                        else:
                            _logger.warning("Error returned by server with code: %s and message: %s" % (content, ird_api_codes[int(content)]))
                        if int(content) in [200,101]:
                            invoice.write({'sent_to_ird': True, 'is_ird_realtime': data["isrealtime"]})
                    except requests.HTTPError:
                        raise UserError(_("The IRD server cannot be found. Maybe it has been moved to new IP."))
            except Exception as e:
                failure_reason = tools.ustr(e)
                _logger.exception('failed sending invoice (id: %s) due to %s', invoice.id, failure_reason)

            if auto_commit is True:
                self._cr.commit()
        return True
