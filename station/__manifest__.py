# -*- coding: utf-8 -*-
{
    'name': "Station",

    'summary': """
        Oil Warehouse Station (Location)""",

    'author': "Ygen Software Pvt. Ltd.",
    'website': "https://ygen.io",
    'contributors': [
        "Ashim Bajracharya <ashimbazracharya@gmail.com>",
    ],

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '11.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/station.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}