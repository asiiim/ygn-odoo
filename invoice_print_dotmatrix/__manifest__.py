# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.
{
    'name': 'Print Invoices designed for dot matrix printers',
    'summary': 'Invoice has been designed specifically for dot matrix printers.',
    'version': '11.0.1.0.0',
    'author': 'Ygen Software Pvt. Ltd.',
    'category': 'Accounting',
    'license': 'OPL-1',
    'complexity': 'normal',
    'website': "https://ygen.io",
    'depends': ['account_invoicing'],
    'data': [
        'views/report_invoice.xml',
        'views/account_report.xml',
    ],
    'auto_install': False,
    'installable': True,
}
