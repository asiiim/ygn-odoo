# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import Response
from odoo.http import request
from operator import itemgetter

import logging
_logger = logging.getLogger(__name__)


class ResPartnerController(http.Controller):

    @http.route('/api/invoice/customer', type='json', auth='public', methods=['POST'], csrf=False)
    def create_partner(self, db, username, password, name, mobile, phone, tin, **args):

        # Login in:
        try:
            request.session.authenticate(db, username, password)
        except Exception as e:
            # Invalid Login:
            info = "Logging Error {}".format((e))
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

        partner = request.env['res.partner']
        customer = partner.search([('name', '=', name), ('mobile', '=', mobile)])
        if not customer:
            vals = {
                'name': name,
                'mobile': mobile,
                'phone': phone,
                'vat': tin
            }
            new_customer = partner.create(vals)
            return {
                "code": 200,
                "message": "Contacts created successfully...",
                "id": new_customer.id,
                "name": new_customer.name
            }
            
        else:
            return {
                "code": 202,
                "message": "The contacts you try to create is already existed...",
            }

