# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class account_payment(models.Model):
    _inherit = 'account.payment'

    move_reconciled = fields.Boolean(compute="_get_move_reconciled", readonly=True, store=True)
    sale_id = fields.Many2one('sale.order', 'Ret. Adv SO')
    adv_sale_id = fields.Many2one('sale.order', 'Adv. SO')

    is_migrated = fields.Boolean('Migrated', default=False, copy=False, track_visibility='onchange')

    @api.model
    def update_order_advance_payment(self):
        payments = self.env['account.payment'].search([('is_migrated', '=', False)], limit=300)
        for payment in payments:
            _logger.warning(payment.id)
            wordset = payment.communication.split()
            sale_id_ref = wordset[-1]
            sale_order = self.env['sale.order'].search([('name', '=', sale_id_ref)])
            if 'Return' in wordset or 'return' in wordset:
                payment.write({
                    'sale_id': sale_order.id,
                    'is_migrated': True
                })
                sale_order.write({'is_adv_return': True})
            else:
                payment.write({
                    'adv_sale_id': sale_order.id,
                    'is_migrated': True
                })
                sale_order.write({'is_adv': True})
