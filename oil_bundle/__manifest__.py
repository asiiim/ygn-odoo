# -*- coding: utf-8 -*-
{
    'name': "Oil Gasoline Bundles",

    'summary': """
        Bundles of the elements needed for the oil & gasonline business""",

    'author': "Ygen Software Pvt. Ltd.",
    'website': "https://ygen.io",
    'contributors': [
        "Ashim Bajracharya <ashim@ygen.io>",
    ],

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Oil & Gasoline',
    'version': '11.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 
        'partner_company_chamber', 
        'sale_invoice_vehicle',
        'invoice_report_vehicle_chamber',
        'sale_management',
        'account_invoicing',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}