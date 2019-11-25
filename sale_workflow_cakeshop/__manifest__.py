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
    # price
    'price': 1500.00,
    'currency': 'EUR',
    'depends': ['sale', 'stock', 'account_payment', 'kitchen_order', 'kitchen_order_note', 'ygen_partner_delivery_zone'],
    'data': [
        'views/sale_views.xml',
        'views/product_views.xml',
        'views/account_invoice.xml',
        'views/account_payment.xml',
        'views/res_company.xml',
        'views/res_config_settings.xml',
        'wizards/product_configurator_order_now.xml',
        'wizards/sale_make_invoice_advance_views.xml',
        'wizards/sale_requested_date.xml',
        'wizards/sale_change_advance.xml',
        'wizards/sale_change_customer.xml',
        'report/kitchen_sale_order_report.xml'
    ],
    # 'images': ['static/description/banner.png'],
}
