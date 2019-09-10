# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    'name': "Kitchen Order",

    'summary': """
        Kitchen orders can be generated from the Sales Order confirmation.""",

    'author': "Ygen Software Pvt. Ltd.",
    'website': "https://ygen.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Product',
    'license': 'OPL-1',
    'version': '11.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management', 'sale_order_dates'],

    # always loaded
    'data': [
        'security/kitchen_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/kitchen_order_stage.xml',
        'views/kitchen_order.xml',
        'views/kitchen_order_stage.xml',
        'report/kitchen_order_report.xml'
    ],
}