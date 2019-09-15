# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    'name': 'Nepal - IRD Integration',
    'version': '1.0',
    'author': 'Ygen Software Pvt. Ltd.',
    'website': 'http://ygen.io',
    'category': 'Localization',
    'description': """
This module syncs invoices and invoices return to IRD.
==============================================================================

    """,
    'depends': ['keychain','l10n_np','l10n_np_sales'],

    # price
    'price': 600.00,
    'currency': 'EUR',

    'data': [
        'views/res_config_settings_views.xml',
        'views/res_company_views.xml',
        'data/invoice_data.xml',
    ],
}
