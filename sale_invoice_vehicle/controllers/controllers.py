# -*- coding: utf-8 -*-
from odoo import http

# class SaleInvoiceVehicle(http.Controller):
#     @http.route('/sale_invoice_vehicle/sale_invoice_vehicle/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_invoice_vehicle/sale_invoice_vehicle/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_invoice_vehicle.listing', {
#             'root': '/sale_invoice_vehicle/sale_invoice_vehicle',
#             'objects': http.request.env['sale_invoice_vehicle.sale_invoice_vehicle'].search([]),
#         })

#     @http.route('/sale_invoice_vehicle/sale_invoice_vehicle/objects/<model("sale_invoice_vehicle.sale_invoice_vehicle"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_invoice_vehicle.object', {
#             'object': obj
#         })