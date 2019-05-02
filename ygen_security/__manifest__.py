# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.
{
    'name': "Ygen Security",

    'summary': """
        Ygen Security for the database backup and deletion""",

    'author': "Ygen Software Pvt. Ltd.",
    'website': "https://ygen.io",
    'contributors': [
        "Ashim Bajracharya <ashimbazracharya@gmail.com>",
    ],

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '11.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # price
    'price': 300.00,
    'currency': 'EUR',

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'data/db_expiration_datetime.xml',
        # 'views/res_config_settings.xml'
    ],
}