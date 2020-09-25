# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.
{
    'name': 'Ygen Order Ticket Dot Matrix Print',
    'summary': 'Order has been designed specifically for dot matrix printers.',
    'version': '11.0.1.0.0',
    'author': 'Aashim Bajracharya, Ygen Software Pvt. Ltd.',
    'category': 'Accounting',
    'license': 'OPL-1',
    'complexity': 'normal',
    'website': "https://ygen.io",
    'depends': ['base', 'ygen_sale_order_flow', 'ygen_saleflow_advance_payment'],
    'data': [
        'views/report_order_ticket.xml',
        'views/order_ticket_report.xml'
    ],
    'auto_install': False,
    'installable': True,
}
