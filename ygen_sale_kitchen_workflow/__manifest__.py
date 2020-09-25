# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    'name': "BakingSoft",

    'summary': """
        Integrate Kitchen with Sale Workflow.""",

    'author': "Aashim Bajracharya, Ygen Software Pvt. Ltd.",
    'website': "https://ygen.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sale',
    'license': 'OPL-1',
    'version': '11.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['kitchen_order', 'kitchen_order_note', 'ygen_sale_order_flow', 'ygen_order_print_dotmatrix'],

    # always loaded
    'data': [
        'wizards/ygen_order_now.xml',
        'views/kitchen_order.xml',
        'views/sale.xml',
        'views/views.xml',
        'reports/kitchen_sale_order_report.xml'
    ]
}
