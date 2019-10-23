# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.
{
    'name': 'Order Ticket Dot Matrix Print',
    'summary': 'Order has been designed specifically for dot matrix printers.',
    'version': '11.0.1.0.0',
    'author': 'Ygen Software Pvt. Ltd.',
    'category': 'Accounting',
    'license': 'OPL-1',
    'complexity': 'normal',
    'website': "https://ygen.io",
    'depends': ['base', 'sale', 'sale_workflow_cakeshop'],
    'data': [
        'views/report_order_ticket.xml',
        'views/order_ticket_report.xml'
    ],
    'auto_install': False,
    'installable': True,
}
