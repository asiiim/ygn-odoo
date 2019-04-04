# -*- coding: utf-8 -*-
from odoo import http

# class Storage(http.Controller):
#     @http.route('/storage/storage/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/storage/storage/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('storage.listing', {
#             'root': '/storage/storage',
#             'objects': http.request.env['storage.storage'].search([]),
#         })

#     @http.route('/storage/storage/objects/<model("storage.storage"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('storage.object', {
#             'object': obj
#         })