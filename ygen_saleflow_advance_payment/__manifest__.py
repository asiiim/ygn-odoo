# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    'name': "Ygen Sale Order Flow Advance Payment",
    'summary': """ Advance Payment in Sale Flow.""",
    'version': '11.0.1.0.0',
    'author': 'Ygen Software Pvt. Ltd.',
    'website': 'https://ygen.io',
    'category': 'Sales',
    'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': ['ygen_sale_order_flow', 'account_payment'],

    # always loaded
    'data': [
        'wizards/ygen_order_now.xml',
        'wizards/sale_change_advance.xml',
        'views/sale.xml'
    ]
}