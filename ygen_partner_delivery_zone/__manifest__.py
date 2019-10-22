# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    'name': "Ygen Partner Delivery Zone",

    'summary': """Partner delivery zone based on OCA Module""",

    'author': "Ygen Software Pvt. Ltd.",
    'website': "https://ygen.io",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Delivery',
    'license': 'OPL-1',
    'version': '11.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'partner_delivery_zone'],

    # price
    'price': 200.00,
    'currency': 'EUR',

    # always loaded
    'data': [
        'views/partner.xml'
    ]
}