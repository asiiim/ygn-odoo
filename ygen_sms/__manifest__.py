# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.
{
    'name': "Ygen SMS Service",

    'summary': """
        Send single or bulk sms.""",

    'author': "Ygen Software Pvt. Ltd.",
    'website': "https://ygen.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Contact',
    'version': '11.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'base_setup'],

    # price
    'price': 30.00,
    'currency': 'EUR',

    # always loaded
    'data': [
        'security/sms_security.xml',
        'security/ir.model.access.csv',
        'data/sms_credit.xml',
        'data/ir_sequence.xml',
        'views/single_sms_views.xml',
        'views/res_config_settings_views.xml',
        'views/messaging_list_views.xml',
        'views/multiple_sms_views.xml',
        'views/sms_credit.xml',
    ],
}
