# -*- coding: utf-8 -*-
{
    'name': "custom_filters",

    'summary': """
        Custome filter to filter the list view with search view
        """,

    'description': """
        Adding custom filter to filter the search view  like today's invoice, today sale ,etc.
    """,

    'author': "Ygen Software Pvt.Ltd",
    'website': "https://www.ygen.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Filters',
    'version': '11.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/filters.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}