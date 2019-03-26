# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    tanker_vehicle_number = fields.Char('Vehicle No.')

    # Override method to pass tanker vehicle number in the dictionary 
    # before creating invoice object of the respective sale order line
    # if the invoice advance payment is of type delivered or deduct down
    # payments.
    def _prepare_invoice(self):
	    invoice_vals = super(SaleOrder, self)._prepare_invoice()
	    invoice_vals.update({
	        'tanker_vehicle_number': self.tanker_vehicle_number,
	    })
	    return invoice_vals
