# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    vehicle_id = fields.Many2one('vehicle.vehicle', string="Vehicle", ondelete='restrict')

    # Override method to pass tanker vehicle number in the dictionary 
    # before creating invoice object of the respective sale order line
    # if the invoice advance payment is of type delivered or deduct down
    # payments.
    @api.multi
    def _prepare_invoice(self):
	    invoice_vals = super(SaleOrder, self)._prepare_invoice()
	    invoice_vals.update({'vehicle_id': self.vehicle_id.id})
	    return invoice_vals
