# -*- coding: utf-8 -*-
from odoo import http

# class CustomChatterReport(http.Controller):
#     @http.route('/custom_chatter_report/custom_chatter_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_chatter_report/custom_chatter_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_chatter_report.listing', {
#             'root': '/custom_chatter_report/custom_chatter_report',
#             'objects': http.request.env['custom_chatter_report.custom_chatter_report'].search([]),
#         })

#     @http.route('/custom_chatter_report/custom_chatter_report/objects/<model("custom_chatter_report.custom_chatter_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_chatter_report.object', {
#             'object': obj
#         })