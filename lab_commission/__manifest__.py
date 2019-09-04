# -*- coding: utf-8 -*-
{
    'name': "lab_commission",

    'summary': """
        Calculated commission for lab """,

    'description': """
        This module calculate and show the commission of related clinic.
    """,

    'author': "Ygen",
    'website': "https://www.ygen.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Commission',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/res_partner_extend_views.xml',
        'views/account_invoice_extend_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}