# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.
{
    'name': "Medical Lab Product Appointment",

    'summary': """
        Provide to select product for the lab test during invoicing.""",

    'author': "Ygen Software Pvt. Ltd.",
    'website': "https://ygen.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Product',
    'version': '11.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['medical_lab_management', 'product_analytic'],

    # price
    'price': 30.00,
    'currency': 'EUR',

    # always loaded
    'data': [
        'views/lab_test.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}