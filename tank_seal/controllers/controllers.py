# -*- coding: utf-8 -*-
from odoo import http

# class TankSeal(http.Controller):
#     @http.route('/tank_seal/tank_seal/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tank_seal/tank_seal/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tank_seal.listing', {
#             'root': '/tank_seal/tank_seal',
#             'objects': http.request.env['tank_seal.tank_seal'].search([]),
#         })

#     @http.route('/tank_seal/tank_seal/objects/<model("tank_seal.tank_seal"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tank_seal.object', {
#             'object': obj
#         })