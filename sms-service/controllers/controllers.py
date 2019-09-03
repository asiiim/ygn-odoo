# -*- coding: utf-8 -*-
from odoo import http

# class Sms-service(http.Controller):
#     @http.route('/sms-service/sms-service/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sms-service/sms-service/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sms-service.listing', {
#             'root': '/sms-service/sms-service',
#             'objects': http.request.env['sms-service.sms-service'].search([]),
#         })

#     @http.route('/sms-service/sms-service/objects/<model("sms-service.sms-service"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sms-service.object', {
#             'object': obj
#         })