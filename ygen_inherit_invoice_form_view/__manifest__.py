# -*- coding: utf-8 -*-
{
    'name': "Reduced Invoice Form View",

    'summary': """
        Hide unnecessary fields in the invoice form views""",

    'author': "Ygen Software Pvt. Ltd.",
    'website': "https://ygen.io",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Account',
    'license': 'OPL-1',
    'version': '11.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # price
    'price': 200.00,
    'currency': 'EUR',

    'data': [
        'views/account_invoice.xml'
    ]
}