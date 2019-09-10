# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    'name': 'Advanced Sales Workflow for Cake shops',
    'version': '1.0',
    'author': 'Ygen Software Pvt. Ltd.',
    'website': 'https://ygen.io',
    'category': 'Sales',
    'description': """
This module helps salesperson in a cake shop to select product attributes, 
kitchen order notes, advance payment, and customer information in a series of 
steps rather than going through multiple separate windows. This module is only 
good for processing one product at a time.
    """,
    'installable': True,
    'application': True,
    'auto_install': False,
    'depends': ['sale','account_payment', 'kitchen_order', 'kitchen_order_note', 'product_configurator'],
    'data': [
        'views/product_views.xml',
        # 'views/sale_views.xml',
        'wizards/product_configurator_order_now.xml',
    ],
    # 'images': ['static/description/banner.png'],
}
