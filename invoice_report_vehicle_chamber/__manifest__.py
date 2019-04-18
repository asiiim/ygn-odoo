# -*- coding: utf-8 -*-
{
    'name': "Invoice Vehicle and Chamber Numbers",

    'summary': """
        Consists of vehicle and chamber number in invoice report document""",

    'author': "Ygen Software Pvt. Ltd.",
    'website': "https://ygen.io",
    'contributors': [
        "Ashim Bajracharya <ashim@ygen.io>",
    ],

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Industries',
    'version': '11.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'partner_company_chamber', 'tank_seal',],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'report/invoice_report_templates.xml',
    ],
}