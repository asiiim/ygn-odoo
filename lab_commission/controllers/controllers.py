# -*- coding: utf-8 -*-
from odoo import http

# class LabCommission(http.Controller):
#     @http.route('/lab_commission/lab_commission/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/lab_commission/lab_commission/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('lab_commission.listing', {
#             'root': '/lab_commission/lab_commission',
#             'objects': http.request.env['lab_commission.lab_commission'].search([]),
#         })

#     @http.route('/lab_commission/lab_commission/objects/<model("lab_commission.lab_commission"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('lab_commission.object', {
#             'object': obj
#         })