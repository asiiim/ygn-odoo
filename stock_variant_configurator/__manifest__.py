# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.
{
    'name': "Stock Variant Configurator",
    'version': '11.0.1.0.0',
    'author': 'Ygen Software Pvt. Ltd.',
    'website': 'https://ygen.io',
    'category': 'Stock',
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 1500.00,
    'currency': 'EUR',
    'depends': ['stock', 'product_variant_configurator'],
    'data': [
        'views/stock_inventory.xml',
        'views/stock_picking.xml'
    ]
}
