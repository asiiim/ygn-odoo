# -*- coding: utf-8 -*-
from odoo import http

# class OilBundle(http.Controller):
#     @http.route('/oil_bundle/oil_bundle/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/oil_bundle/oil_bundle/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('oil_bundle.listing', {
#             'root': '/oil_bundle/oil_bundle',
#             'objects': http.request.env['oil_bundle.oil_bundle'].search([]),
#         })

#     @http.route('/oil_bundle/oil_bundle/objects/<model("oil_bundle.oil_bundle"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('oil_bundle.object', {
#             'object': obj
#         })