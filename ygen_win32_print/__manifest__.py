# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.
{
    'name': "Ygen Win32 Direct Print",

    'summary': """
        Print file directly in Windows OS.""",

    'author': "Ygen Software Pvt. Ltd.",
    'website': "https://ygen.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Report',
    'license': 'OPL-1',
    'version': '11.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'portal'],

    # price
    'price': 200.00,
    'currency': 'EUR',

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/ygen_printer.xml',
        'views/ir_actions_report.xml'
    ],
}
