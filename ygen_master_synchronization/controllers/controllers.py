# -*- coding: utf-8 -*-
from odoo import http

# class YgenMasterSynchronization(http.Controller):
#     @http.route('/ygen_master_synchronization/ygen_master_synchronization/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ygen_master_synchronization/ygen_master_synchronization/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ygen_master_synchronization.listing', {
#             'root': '/ygen_master_synchronization/ygen_master_synchronization',
#             'objects': http.request.env['ygen_master_synchronization.ygen_master_synchronization'].search([]),
#         })

#     @http.route('/ygen_master_synchronization/ygen_master_synchronization/objects/<model("ygen_master_synchronization.ygen_master_synchronization"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ygen_master_synchronization.object', {
#             'object': obj
#         })