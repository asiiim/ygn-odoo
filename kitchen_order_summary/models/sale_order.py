# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import Warning, ValidationError, UserError

import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def validate_picking(self):
        super(SaleOrder, self).validate_picking()
        
        # Unlink custom images of kitchen orders
        for so in self:
            for ko in so.kitchen_order_ids:
                if ko.custom_image or ko.secondary_custom_image:
                    ko.write({'flush_custom_images': True})
