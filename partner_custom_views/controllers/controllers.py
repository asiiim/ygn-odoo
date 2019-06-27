# -*- coding: utf-8 -*-
from odoo import http

# class PartnerCustomViews(http.Controller):
#     @http.route('/partner_custom_views/partner_custom_views/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/partner_custom_views/partner_custom_views/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('partner_custom_views.listing', {
#             'root': '/partner_custom_views/partner_custom_views',
#             'objects': http.request.env['partner_custom_views.partner_custom_views'].search([]),
#         })

#     @http.route('/partner_custom_views/partner_custom_views/objects/<model("partner_custom_views.partner_custom_views"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('partner_custom_views.object', {
#             'object': obj
#         })