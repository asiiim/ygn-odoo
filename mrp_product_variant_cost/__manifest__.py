# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    'name': 'Update Product Cost in Manufacture Order',
    'version': '11.0.1.0.0',
    'author': 'Ygen Software Pvt. Ltd.',
    'website': 'https://ygen.io',
    'category': 'MRP',
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 1500.00,
    'currency': 'EUR',
    'depends': ['mrp'],
    'data': [
        'wizards/update_product_cost.xml',
        'views/mrp_production.xml'
    ],
}
