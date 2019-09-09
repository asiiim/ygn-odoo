# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    'name': "Ygen HR Payslip Libraries",

    'summary': """
        Additional essential libraries for hr payslip.    
    """,

    'author': "Ygen Software Pvt. Ltd.",
    'website': "https://ygen.io",
    
    'installable': True,
    'application': True,
    'auto_install': False,

    # Categories can be used to filter modules in modules listing
    'category': 'Hr',
    'version': '11.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_payroll'],

    # always loaded
    'data': [
        'views/hr_payslip.xml'
    ],
}