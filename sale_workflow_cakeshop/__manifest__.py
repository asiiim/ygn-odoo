# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    'name': 'Advanced Sales Workflow for Cake shops',
    'version': '11.0.1.0.0',
    'author': 'Ygen Software Pvt. Ltd.',
    'website': 'https://ygen.io',
    'category': 'Sales',
    'license': 'OPL-1',
    'description': """
This module helps salesperson in a cake shop to select product attributes, 
kitchen order notes, advance payment, and customer information in a series of 
steps rather than going through multiple separate windows. This module is only 
good for processing one product at a time.
    """,
    'installable': True,
    'application': True,
    'auto_install': False,
    'depends': ['sale', 'stock', 'account_payment', 'kitchen_order', 'kitchen_order_note', 'product_configurator'],
    'data': [
        'views/product_views.xml',
        'views/sale_views.xml',
        'views/account_invoice.xml',
        'wizards/product_configurator_order_now.xml',
        'wizards/sale_make_invoice_advance_views.xml',
        'report/kitchen_sale_order_report.xml'
    ],
    # 'images': ['static/description/banner.png'],
}
