# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.
{
    'name': "Ygen Slave Synchronization",

    'summary': """
        Receive data from the master synchronizer.""",

    'author': "Ygen Software Pvt. Ltd.",
    'website': "https://ygen.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Invoice',
    'license': 'OPL-1',
    'version': '11.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # price
    'price': 200.00,
    'currency': 'EUR',

    # always loaded
    'data': [
        # 'security/sms_security.xml',
        # 'security/ir.model.access.csv',
    ],
}