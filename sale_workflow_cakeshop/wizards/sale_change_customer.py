# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, api, _
from odoo.exceptions import Warning, ValidationError, UserError

import logging

_logger = logging.getLogger(__name__)


class SaleChangeCustomer(models.TransientModel):
    _name = 'sale.change.customer'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True, change_default=True, index=True)

    @api.multi
    def change_customer(self):

        so_obj = self.env['sale.order']
        so = so_obj.browse(self._context.get('active_id'))
        so.write({'partner_id': self.partner_id.id})
