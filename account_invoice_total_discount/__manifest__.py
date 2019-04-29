# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    'name': 'Invoice Total Discount',
    'version': '1.0',
    'author': 'Ygen Software Pvt. Ltd.',
    'website': 'http://ygen.io',
    'category': 'Accounting',
    'description': """
This module adds Total Discount in Invoices.
==============================================================================

    """,
    'installable': True,
    'application': True,
    'auto_install': False,
    'depends': ['base','account_invoicing'],
    'data': ['views/account_invoice_view.xml'],
    'images': ['static/description/banner.png'],
}
