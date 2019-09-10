# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    'name': "Advanced Kitchen Order Notes",

    'summary': """
        Set predefined notes for a kitchen order.""",

    'author': "Ygen Software Pvt. Ltd.",
    'website': "https://ygen.io",

    # Categories can be used to filter modules in modules listing
    'category': 'Sale',
    'license': 'OPL-1',
    'version': '11.0.1.0.0',
    "price": 34.00,
    "currency": "EUR",

    # any module necessary for this one to work correctly
    'depends': ['kitchen_order'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/kitchen_order_notes.xml',
    ],
    "demo": [
        "data/ko_notes_demo.xml",
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,
}