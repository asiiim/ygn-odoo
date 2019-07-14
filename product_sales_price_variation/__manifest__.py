# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.
{
    'name': "Product Sales Price Variation",

    'summary': """
        Product sales price gets changed if certain rate of base products get changed.""",

    'author': "Ygen Software Pvt. Ltd.",
    'website': "https://ygen.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Product',
    'version': '11.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_management'],

    # price
    'price': 30.00,
    'currency': 'EUR',

    # always loaded
    'data': [
        'views/product.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}