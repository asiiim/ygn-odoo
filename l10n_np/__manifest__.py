# -*- coding: utf-8 -*-
{
    'name': 'Nepali - Accounting',
    'version': '2.0',
    'author': 'Ygen Software',
    'website': 'http://ygen.io',
    'category': 'Localization',
    'description': """
This is the base module to manage the accounting chart for Nepal in Odoo.
==============================================================================

    """,
    'depends': ['account_tax_python'],
    'data': [
            'data/res_country_data.xml',
            'data/account_chart_template_data.xml',
            'data/l10n_np_chart_data.xml',
            'data/account_data.xml',
            'data/account_tax_template_data.xml',
            'data/res_country_state_data.xml',
            'data/res_country_district_data.xml',
            'data/account_chart_template_data.yml',
            'data/report_paperformat.xml',
            'data/menuitem_data.xml',
            'views/report_invoice.xml',
            'views/res_country_district_views.xml',
            'views/res_company_views.xml',
            'views/report_templates.xml',
            # 'views/res_partner_views.xml',
    ],
}
