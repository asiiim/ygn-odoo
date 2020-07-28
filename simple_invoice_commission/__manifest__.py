# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.
{
    'name': "Simple Invoice Commission",

    'summary': """
        Calculated lab commission """,

    'description': """
        Calculate commission for each referral in the lab.
    """,

    'author': "Ygen Software Pvt. Ltd.",
    'website': "https://www.ygen.io",
    'category': 'Invoicing',
    'version': '11.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account', 'account_invoicing'],

    # always loaded
    'data': [
        'views/res_partner_extend_views.xml',
        'views/account_invoice_extend_views.xml',
        'views/res_config_settings.xml',
        'reports/account_invoice_report_views.xml'
    ],
}