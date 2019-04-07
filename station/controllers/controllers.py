# -*- coding: utf-8 -*-
from odoo import http

# class Station(http.Controller):
#     @http.route('/station/station/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/station/station/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('station.listing', {
#             'root': '/station/station',
#             'objects': http.request.env['station.station'].search([]),
#         })

#     @http.route('/station/station/objects/<model("station.station"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('station.object', {
#             'object': obj
#         })