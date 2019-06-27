# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.
{
    'name': "custom_chatter_report",

    'summary': """
       Print all the report of the chatter activities""",

    'description': """
        All the activities like log note, message and schedule activities of the form
        can be printed with this modules.
    """,

    'author': "Ygen Software",
    'website': "https://ygen.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Report',
    'version': '11.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'portal'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/chatter_report.xml',
        'views/report_res_partner_chatter.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}