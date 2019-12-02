# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    'name': "Google Driver File Link",

    'summary': """
        Enter public link to the file in google and use that link 
        in other modules. One common example could be images""",

    'author': "Ygen Software Pvt. Ltd.",
    'website': "https://ygen.io",

    # Categories can be used to filter modules in modules listing
    'category': 'Extra Tools',
    'license': 'OPL-1',
    'version': '11.0.1.0.0',
    "price": 100.00,
    "currency": "EUR",

    # any module necessary for this one to work correctly
    'depends': ['web'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/drive_file_view.xml',
    ],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,
}