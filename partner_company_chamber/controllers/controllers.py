# -*- coding: utf-8 -*-
from odoo import http

# class PartnerCompanyChamber(http.Controller):
#     @http.route('/partner_company_chamber/partner_company_chamber/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/partner_company_chamber/partner_company_chamber/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('partner_company_chamber.listing', {
#             'root': '/partner_company_chamber/partner_company_chamber',
#             'objects': http.request.env['partner_company_chamber.partner_company_chamber'].search([]),
#         })

#     @http.route('/partner_company_chamber/partner_company_chamber/objects/<model("partner_company_chamber.partner_company_chamber"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('partner_company_chamber.object', {
#             'object': obj
#         })