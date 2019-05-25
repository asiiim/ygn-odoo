# -*- coding: utf-8 -*-
{
    'name': "partner_custom_views",

    'summary': """
        Here we change a view accoriding to our partner""",

    'description': """
        Some of the requirement of our client is change and we need to extend our
        view to fuilfilled their requirement.
    """,

    'author': "Ygen Software",
    'website': "https://www.ygen.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Partner',
    'version': '11.0',

    # any module necessary for this one to work correctly
    'depends': ['base','contacts'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/res_partner_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}