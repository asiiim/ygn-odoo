# -*- coding: utf-8 -*-
from odoo import http

# class MedicalLabProductAppointment(http.Controller):
#     @http.route('/medical_lab_product_appointment/medical_lab_product_appointment/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/medical_lab_product_appointment/medical_lab_product_appointment/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('medical_lab_product_appointment.listing', {
#             'root': '/medical_lab_product_appointment/medical_lab_product_appointment',
#             'objects': http.request.env['medical_lab_product_appointment.medical_lab_product_appointment'].search([]),
#         })

#     @http.route('/medical_lab_product_appointment/medical_lab_product_appointment/objects/<model("medical_lab_product_appointment.medical_lab_product_appointment"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('medical_lab_product_appointment.object', {
#             'object': obj
#         })