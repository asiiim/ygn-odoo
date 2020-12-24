# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    'name': "Sale Order Memo",

    'summary': """
        Add memo for the sale order.""",

    'description': """
        Add memo such as reference or other notes/remarks regarding the sale order.
    """,

    'author': "Aashim Bajracharya, Ygen Software Pvt. Ltd.",
    'email': "ygennepal@gmail.com",

    'category': 'Sale',
    'version': '11.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        'views/sale_order.xml'
    ],

    'installable': True
}