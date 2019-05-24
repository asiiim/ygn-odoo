# -*- coding: utf-8 -*-
from odoo import http

# class CustomFilters(http.Controller):
#     @http.route('/custom_filters/custom_filters/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_filters/custom_filters/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_filters.listing', {
#             'root': '/custom_filters/custom_filters',
#             'objects': http.request.env['custom_filters.custom_filters'].search([]),
#         })

#     @http.route('/custom_filters/custom_filters/objects/<model("custom_filters.custom_filters"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_filters.object', {
#             'object': obj
#         })