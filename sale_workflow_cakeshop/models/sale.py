# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_id = fields.Many2one(
        comodel_name='account.payment',
        # required=True,
        readonly=True
    )
    advance_payment = fields.Monetary(related="payment_id.amount", string="Advance", store=True)
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
            if not line.invoice_ids:
                # Check if the payment linked has already been matched 
                # and set the amount_due accordingly
                line.amount_due = line.amount_total - (line.payment_id.amount if line.payment_id.state == 'posted' and not line.payment_id.move_reconciled else 0)
            else:
                for invoice in line.invoice_ids:
                    line.amount_due = invoice.residual
                    break

    # Stock Picking Operation
    delivery_validated = fields.Boolean('Delivery Validated?', default=False, readonly=True, copy=False)

    @api.multi
    def validate_picking(self):
        stock_picking = self.env['stock.picking'].search([('origin', '=', self.name)], limit=1)
        stock_picking.button_validate()
        if stock_picking.state == "done":
            self.write({'delivery_validated': True})

    # Tender and Change
    tender_amount = fields.Monetary(string='Tender', track_visibility='always', default=0.0)
    change_amount = fields.Monetary(string='Change', track_visibility='always', default=0.0)

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        invoice_ids_arr = super(SaleOrder, self).action_invoice_create(grouped, final)
        invoice_ids = self.env['account.invoice'].browse(invoice_ids_arr)
        for inv in invoice_ids:
            inv.write({
                'tender_amount': self.tender_amount,
                'change_amount': self.change_amount
            })
        return invoice_ids_arr

    # print option selection for KO & SO
    kitchen_sale_order_print_selection = fields.Selection([('ko', 'Kitchen Order'), ('so', 'Sale Order'), ('both', 'Both')], string="Print Sale Order or Kitchen Order?", default="both")

    # print SO or KO
    @api.multi
    def print_koso_report(self):
        return self.env.ref('sale_workflow_cakeshop.action_report_sale_or_kitchen_order').report_action(self)

    # view related kitchen orders of the sale order
    @api.multi
    def view_kitchen_order(self):
        ko_id = []
        
        for ko in self.kitchen_order_ids:
            ko_id.append(ko.id)
        
        return {
            'name': _('Kitchen Order'),
            'res_model': 'kitchen.order',
            'res_id': ko_id[0],
            'views': [(self.env.ref('kitchen_order.view_kitchen_order_form').id, 'form')],
            'type': 'ir.actions.act_window',
            'target':'new'
        }
