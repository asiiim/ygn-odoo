# -*- coding: utf-8 -*-
from odoo import http

# class CustomFiltersStock(http.Controller):
#     @http.route('/custom_filters_stock/custom_filters_stock/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_filters_stock/custom_filters_stock/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_filters_stock.listing', {
#             'root': '/custom_filters_stock/custom_filters_stock',
#             'objects': http.request.env['custom_filters_stock.custom_filters_stock'].search([]),
#         })

#     @http.route('/custom_filters_stock/custom_filters_stock/objects/<model("custom_filters_stock.custom_filters_stock"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_filters_stock.object', {
#             'object': obj
#         })