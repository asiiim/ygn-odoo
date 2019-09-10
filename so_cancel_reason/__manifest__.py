# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.
{
    'name': 'Sale Cancel Reason',
    'version': '11.0.1.0.0',
    'author': 'Ygen Software Pvt. Ltd.',
    'category': 'Sale',
    'license': 'OPL-1',
    'complexity': 'normal',
    'website': "https://ygen.io",
    'depends': ['sale'],
    'data': [
        'wizard/cancel_reason_view.xml',
        'view/sale_view.xml',
        'security/ir.model.access.csv',
        'data/sale_order_cancel_reason.xml',
    ],
    'auto_install': False,
    'installable': True,
}
