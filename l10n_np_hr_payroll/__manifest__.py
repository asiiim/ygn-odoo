# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.
{
    'name': "Nepali Payroll",
    'version': '2.0',
    'author': 'Ygen Software Pvt. Ltd.',
    'website': 'http://ygen.io',
    'category': 'Localization',

    # any module necessary for this one to work correctly
    'depends': ['account_tax_python', 'contacts', 'hr_payroll'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/l10n_np_hr_payroll.xml',
        'data/l10n_np_hr_payroll_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}