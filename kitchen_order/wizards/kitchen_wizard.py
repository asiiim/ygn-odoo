# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class KitchenRequestedDateWizard(models.TransientModel):
    _name = "kitchen.requested.date.wizard"

    new_req_date = fields.Datetime(string='New Requested Date', default=fields.Datetime.now)

    @api.multi
    def change_requested_date(self):
        
        self.ensure_one()
        ko_obj = self.env['kitchen.order']
        so_obj = self.env['sale.order']

        ko = ko_obj.browse(self._context.get('active_id'))
        so = so_obj.search([('id', '=', ko.saleorder_id.id)])

        so.write({
            'requested_date': self.new_req_date
        })