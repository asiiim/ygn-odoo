# -*- coding: utf-8 -*-
{
    'name': "Invoice Vehicle Number",

    'summary': """
        Related vehicle number of the sales invoice""",

    'author': "Ygen Software Pvt. Ltd.",
    'website': "https://ygen.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '11.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['vehicle', 'sale', 'account'],

    # always loaded
    'data': [
        'views/sale.xml',
        'views/account_invoice.xml',
        'views/tank_seal_line.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}