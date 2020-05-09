# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    'name': 'eCommerce Kitchen Order Options',
    'category': 'Website',
    'version': '11.0.1.0.0',
    'author': 'Ygen Software Pvt. Ltd.',
    'website': 'https://ygen.io',
    'license': 'OPL-1',
    'description': """
Add message and notes for kitchen order in eCommerce
====================================================

        """,
    'depends': ['website_sale_options'],
    'data': [
        'views/website_sale_options_templates.xml',
    ],
    'qweb': ['static/src/xml/*.xml',],
    'installable': True,
    'price': 150.00,
    'currency': 'EUR',
}
