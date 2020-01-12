# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import Warning, ValidationError, UserError
from odoo.tools import float_is_zero
import math

import logging

_logger = logging.getLogger(__name__)

class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    @api.multi
    def action_validate(self):
        validated = super(StockScrap, self).action_validate()
        if self.production_id:
            for move_raw_id in self.production_id.move_raw_ids:
                if self.product_id == move_raw_id.product_id:
                    if self.scrap_qty > move_raw_id.product_uom_qty:
                        raise UserError(_('There should not be more "scrap qty" than "to consume" in production.'))
                    else:
                        qty_to_update = move_raw_id.product_uom_qty - self.scrap_qty
                        ratio = self.production_id.product_qty / move_raw_id.product_uom_qty
                        self.production_id.update_finished_product_qty(qty_to_update * ratio)
        return validated
