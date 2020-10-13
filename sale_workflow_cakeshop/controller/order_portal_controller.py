# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import content_disposition, dispatch_rpc, request, \
    serialize_exception as _serialize_exception, Response

import logging
_logger = logging.getLogger(__name__)


class OrderPortalController(http.Controller):

    @http.route('/order/portal/<int:id>/', auth="public", website=True)
    def generate_order_portal(self, id, **kw):

        sale_order = request.env['sale.order'].sudo().search([('id', '=', id)])
        return http.request.render('sale_workflow_cakeshop.sale_kitchen_order_portal_report', {
            'docs': sale_order
        })
