# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.
{
    'name': "Ygen Lab Report",

    'summary': """
        Customized Lab Report""",

    'author': "Ygen Software Pvt.Ltd",
    'website': "https://www.ygen.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Report',
    'version': '11.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','medical_lab_management','signature_template'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'report/lab_test_report_headerless.xml',
        'report/lab_test_report.xml',
        'report/report_headerless.xml',
        'report/consolidated_lab_test_reports.xml',
        'report/consolidated_lab_test_reports_header.xml',
        'views/report_templates.xml',
        'views/views.xml',
        'views/lab_request_views.xml',
        'views/lab_specimen_views.xml',
        'views/lab_report_generate_templates.xml'
    ],
}