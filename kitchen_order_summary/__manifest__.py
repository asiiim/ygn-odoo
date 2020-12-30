# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    'name': "Kitchen Order Summary View",

    'summary': """
        Quick view of the kitchen order summary.""",

    'description': """
        Review kitchen order summary as well zoom custom images provided by the client during order.
    """,

    'author': "Aashim Bajracharya, Ygen Software Pvt. Ltd.",
    'email': "ygennepal@gmail.com",

    'category': 'Kitchen',
    'version': '11.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_workflow_cakeshop', 'sale_order_memo'],

    # always loaded
    'data': [
        'views/kitchen_order.xml',
        'wizards/order_now.xml'
    ],

    'installable': True
}