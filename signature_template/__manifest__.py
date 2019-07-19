# -*- coding: utf-8 -*-
{
    'name': "signature_template",

    'summary': """
        Custom Signature Template""",

    'description': """
        Here user define custom signature of the customer.
    """,

    'author': "Ygen Software Pvt.Ltd",
    'website': "https://www.ygen.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Signature',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/signature_views.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}