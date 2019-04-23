# -*- coding: utf-8 -*-
from odoo import http

# class TankChamber(http.Controller):
#     @http.route('/tank_chamber/tank_chamber/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tank_chamber/tank_chamber/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tank_chamber.listing', {
#             'root': '/tank_chamber/tank_chamber',
#             'objects': http.request.env['tank_chamber.tank_chamber'].search([]),
#         })

#     @http.route('/tank_chamber/tank_chamber/objects/<model("tank_chamber.tank_chamber"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tank_chamber.object', {
#             'object': obj
#         })