# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import http, fields
from odoo.http import request
from odoo.addons.website_sale_options.controllers.main import WebsiteSaleOptions
import logging

_logger = logging.getLogger(__name__)


class WebsiteSaleKO(WebsiteSaleOptions):

    @http.route(['/shop/cart/update_option'], type='http', auth="public", methods=['POST'], website=True, multilang=False)
    def cart_options_update_json(self, product_id, add_qty=1, set_qty=0, goto_shop=None, lang=None, **kw):
        r = super(WebsiteSaleKO, self).cart_options_update_json(product_id, add_qty, set_qty, goto_shop, lang, **kw)
        order = request.website.sale_get_order(force_create=True)
        order._cart_update_ko(
            ko_message=kw.get("ko_message"),
            ko_note=kw.get("ko_note"),
            delivery_date=kw.get("delivery_date_tz")
        )
        return r
