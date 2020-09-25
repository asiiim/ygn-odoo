# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    'name': "Ygen Sale Order Flow Fix Discount",
    'summary': """ Provide Fixed Discount in Sale Flow.""",
    'version': '11.0.1.0.0',
    'author': 'Ygen Software Pvt. Ltd.',
    'website': 'https://ygen.io',
    'category': 'Sales',
    'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': ['sale_fixed_discount', 'ygen_sale_order_flow'],

    # always loaded
    'data': [
        'wizards/ygen_order_now.xml'
    ]
}