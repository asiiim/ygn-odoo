# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    'name': "PharmaGen",

    'summary': """
        Online Pharmacy Management System.""",

    'author': "Aashim Bajracharya, Ygen Software Pvt. Ltd.",
    'website': "https://ygen.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sale',
    'license': 'OPL-1',
    'version': '11.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['sale_management', 'stock', 'point_of_sale', 'account_invoicing', 'purchase', 'pos_margin', 'pos_discount', 'pos_reprint', 'dev_global_discount', 'account_invoice_change', 'analytic', 'analytic_partner', 'web_export_view'],

    # always loaded
    'data': [
        'views/views.xml',
    ]
}
