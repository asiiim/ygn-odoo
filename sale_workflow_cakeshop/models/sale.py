# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "sale.order"

    payment_id = fields.Many2one(
        comodel_name='account.payment',
        # required=True,
        readonly=True
    )
    amount_due = fields.Monetary(compute='_compute_amount_due', string='Amount Due', readonly=True)
    kitchen_order_ids = fields.One2many(
        comodel_name='kitchen.order',
        inverse_name='saleorder_id',
        string="Kitchen Orders"
    )

    @api.depends('amount_total')
    def _compute_amount_due(self):
        """
        Compute the amount due of the SO.
        """
        for line in self:
            # Check if the payment linked has already been matched 
            # and set the amount_due accordingly
            line.amount_due = line.amount_total - (line.payment_id.amount if line.payment_id.state == 'posted' and not line.payment_id.move_reconciled else 0)

    # Stock Picking Operation
    delivery_validated = fields.Boolean('Delivery Validated?', default=False, readonly=True, copy=False)

    @api.multi
    def validate_picking(self):
        stock_picking = self.env['stock.picking'].search([('origin', '=', self.name)], limit=1)
        _logger.warning(stock_picking.origin)
        stock_picking.button_validate()
        if stock_picking.state == "done":
            self.write({'delivery_validated': True})

