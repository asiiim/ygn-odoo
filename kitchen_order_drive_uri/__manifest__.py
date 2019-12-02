# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    'name': "Kitchen Order Drive URI Integration",

    'summary': """
        This module integrates Google Drive URI to Kitchen Order.""",

    'author': "Ygen Software Pvt. Ltd.",
    'website': "https://ygen.io",

    # Categories can be used to filter modules in modules listing
    'category': 'Extra Tools',
    'license': 'OPL-1',
    'version': '11.0.1.0.0',
    "price": 50.00,
    "currency": "EUR",

    # any module necessary for this one to work correctly
    'depends': ['drive_file_uri','kitchen_order'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/kitchen_order_report.xml',
        'views/kitchen_order_view.xml',
    ],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,
}