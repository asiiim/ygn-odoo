# -*- coding: utf-8 -*-

import time

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class SaleAdvancePaymentInv(models.TransientModel):

    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        invoice = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)

        invoice.write({
            'tanker_vehicle_number': order.tanker_vehicle_number,
        })

        _logger.warning("=======================================================")
        return invoice
