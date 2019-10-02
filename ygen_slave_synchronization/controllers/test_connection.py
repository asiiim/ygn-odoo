# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import Response
from odoo.http import request
from operator import itemgetter

import logging
_logger = logging.getLogger(__name__)


class TestConnectionController(http.Controller):

    @http.route('/api/test', type='json', auth='public', methods=['POST'], csrf=False)
    def test_connection(self, db, username, password, **args):

        # Login in:
        try:
            request.session.authenticate(db, username, password)
        except Exception as e:
            # Invalid Login:
            info = "Logging Error {}".format((e))
            error = "invalid_login"
            _logger.error(info)
            return {
                'code': 400,
                'message': info,
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
                'message': info,
                'error': error
            }

        return {
            "code": 200,
            "message": "Connection Successfull !",
        }
