# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import content_disposition, dispatch_rpc, request, \
    serialize_exception as _serialize_exception, Response

import logging
_logger = logging.getLogger(__name__)

import requests
from odoo.exceptions import ValidationError

class CustomLabReport(http.Controller):
    def _get_error_message(self, errorcode=None):
        mapping = {
            'missing-input-secret': _('The secret parameter is missing.'),
            'invalid-input-secret':
                _('The secret parameter is invalid or malformed.'),
            'missing-input-response': _('Please click on the reCaptcha below.'),
            'invalid-input-response':
                _('The response parameter is invalid or malformed.'),
        }
        return mapping.get(errorcode, _('There was a problem with '
                                        'the captcha entry.'))

    @http.route('/lab/report', type='http', auth="none", sitemap=False)
    def generate_lab_report(self, redirect=None, **kw):

        values = request.params.copy()
        if request.httprequest.method == 'POST':

            input_appn_id = request.params['appoint_id'].upper()
            input_mobile = request.params['mobile']
            captcha = request.params['g-recaptcha-response']
            if not captcha:
                values['error'] = "Please check the captcha form."
            captcha_secret = "6LcMcaoZAAAAAHzxkuRDCeM7lrqQVeu7JkfMJ5tX"
            url = 'https://www.google.com/recaptcha/api/siteverify'

            ip_addr = request.httprequest.environ.get('HTTP_X_FORWARDED_FOR')
            if ip_addr:
                ip_addr = ip_addr.split(',')[0]
            else:
                ip_addr = request.httprequest.remote_addr

            data = {
                'secret': captcha_secret,
                'response': captcha,
                'remoteip': ip_addr,
            }

            res = requests.post(url, data=data).json()

            error_msg = "\n".join(self._get_error_message(error)
                                for error in res.get('error-codes', []))
            # if error_msg:
            #     values['error'] = error_msg

            if not res.get('success'):
                values['error'] = error_msg
            else:
                appn_id = request.env['lab.appointment'].sudo().search([('name', '=', input_appn_id)])
                patient_id = request.env['lab.patient'].sudo().search([('mobile', '=', input_mobile)])

                lab_request_ids = request.env['lab.request'].sudo().search([('app_id', '=', appn_id.id), ('lab_requestor', '=', patient_id.id)])    
                if lab_request_ids:
                    pdf, _ = request.env.ref('custom_lab_report.consolidated_print_lab_test_header').sudo().render_qweb_pdf(lab_request_ids.ids)
                    pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
                    return request.make_response(pdf, headers=pdfhttpheaders)

                values['error'] = "Wrong Appointment ID/Mobile Number"

        response = request.render('custom_lab_report.generate_lab_report', values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
