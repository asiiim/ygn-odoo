# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class Picking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def button_validate(self):
        _logger.warning(self.state)
        if self.state == "confirmed":
            for moveline in self.move_lines:
                _logger.warning(moveline)
                if moveline.product_uom_qty:
                    moveline.quantity_done = moveline.product_uom_qty
            super(Picking, self).button_validate()
