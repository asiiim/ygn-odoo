# -*- coding: utf-8 -*-
from odoo import http

# class CustomLabReport(http.Controller):
#     @http.route('/custom_lab_report/custom_lab_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_lab_report/custom_lab_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_lab_report.listing', {
#             'root': '/custom_lab_report/custom_lab_report',
#             'objects': http.request.env['custom_lab_report.custom_lab_report'].search([]),
#         })

#     @http.route('/custom_lab_report/custom_lab_report/objects/<model("custom_lab_report.custom_lab_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_lab_report.object', {
#             'object': obj
#         })