# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    'name': "Ygen Sale Order Simplified Invoice",
    'summary': """ Simplified Invoice in Sale Flow.""",
    'version': '11.0.1.0.0',
    'author': 'Ygen Software Pvt. Ltd.',
    'website': 'https://ygen.io',
    'category': 'Sales',
    'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': ['account_invoicing', 'ygen_saleflow_advance_payment'],

    # always loaded
    'data': [
        'wizards/sale_make_invoice.xml',
        'views/sale.xml',
        'views/account_invoice.xml'
    ]
}