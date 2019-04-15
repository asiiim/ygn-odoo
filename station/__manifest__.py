# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.
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
    'depends': ['base', 'stock', 'storage'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/station.xml',
        'views/diptest_wizard.xml',
        'views/res_config_settings.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}