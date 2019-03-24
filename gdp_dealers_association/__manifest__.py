# -*- coding: utf-8 -*-
{
    'name': "Gandaki/Dhaulagiri Petroleum Dealers Association",

    'summary': """
        Add partner company chamber and invoice vehicle number.""",

    'author': "Ygen Software Pvt. Ltd.",
    'website': "https://ygen.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Petrol',
    'version': '11.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'partner_company_chamber', 'sale_invoice_vehicle'],

    'installable': True,
    'application': True,
    'auto_install': True,
}