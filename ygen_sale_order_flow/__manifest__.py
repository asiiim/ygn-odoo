# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    'name': "Ygen Sale Order Flow",
    'version': '11.0.1.0.0',
    'author': 'Ygen Software Pvt. Ltd.',
    'website': 'https://ygen.io',
    'category': 'Sales',
    'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': ['stock', 'sale_management', 'account'],

    # always loaded
    'data': [
        'wizards/ygen_order_now.xml',
        'views/product.xml',
        'views/sale.xml',
        'wizards/sale_change_customer.xml',
        'wizards/sale_requested_date.xml',
        'wizards/sale_make_invoice_advance_views.xml'
    ]
}