# -*- coding: utf-8 -*-
from odoo import http

# class ProductSalesPriceVariation(http.Controller):
#     @http.route('/product_sales_price_variation/product_sales_price_variation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_sales_price_variation/product_sales_price_variation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_sales_price_variation.listing', {
#             'root': '/product_sales_price_variation/product_sales_price_variation',
#             'objects': http.request.env['product_sales_price_variation.product_sales_price_variation'].search([]),
#         })

#     @http.route('/product_sales_price_variation/product_sales_price_variation/objects/<model("product_sales_price_variation.product_sales_price_variation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_sales_price_variation.object', {
#             'object': obj
#         })