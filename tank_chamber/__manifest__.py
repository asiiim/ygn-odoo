# -*- coding: utf-8 -*-
{
    'name': "Tank Chamber",

    'summary': """
        Chambers of the Tank""",

    'author': "Ygen Software Pvt. Ltd.",
    'website': "https://ygen.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Account',
    'version': '11.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # price
    'price': 30.00,
    'currency': 'EUR',

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        'views/chamber.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}