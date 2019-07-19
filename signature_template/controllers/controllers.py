# -*- coding: utf-8 -*-
from odoo import http

# class SignatureTemplate(http.Controller):
#     @http.route('/signature_template/signature_template/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/signature_template/signature_template/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('signature_template.listing', {
#             'root': '/signature_template/signature_template',
#             'objects': http.request.env['signature_template.signature_template'].search([]),
#         })

#     @http.route('/signature_template/signature_template/objects/<model("signature_template.signature_template"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('signature_template.object', {
#             'object': obj
#         })