# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

import datetime
from odoo.exceptions import UserError
from odoo import fields, models, api, _

import logging

_logger = logging.getLogger(__name__)

class LabTestType(models.Model):
    _inherit = "lab.test"

    product_id = fields.Many2one('product.product', string="Product")


class Appointment(models.Model):
    _inherit = "lab.appointment"

    @api.multi
    def create_invoice(self):
        invoice_obj = self.env["account.invoice"]
        invoice_line_obj = self.env["account.invoice.line"]
        for lab in self:
            lab.write({'state': 'to_invoice'})
            if lab.patient_id:
                curr_invoice = {
                    'partner_id': lab.patient_id.patient.id,
                    'account_id': lab.patient_id.patient.property_account_receivable_id.id,
                    'state': 'draft',
                    'type': 'out_invoice',
                    'date_invoice': datetime.datetime.now(),
                    'origin': "Lab Test# : " + lab.name,
                    'target': 'new',
                    'lab_request': lab.id,
                    'is_lab_invoice': True
                }

                inv_ids = invoice_obj.create(curr_invoice)
                inv_id = inv_ids.id

                if inv_ids:
                    journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
                    prd_account_id = journal.default_credit_account_id.id
                    if lab.appointment_lines:
                        for line in lab.appointment_lines:
                            curr_invoice_line = {
                                'name': line.lab_test.product_id.name,
                                'price_unit': line.lab_test.product_id.list_price or 0,
                                'invoice_id': inv_id,
                                'product_id': line.lab_test.product_id.id,
                                'account_id': prd_account_id,
                            }
                            invoice_line_obj.create(curr_invoice_line)

                # self.write({'state': 'invoiced'})
                view_id = self.env.ref('account.invoice_form').id
                return {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'account.invoice',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'name': _('Lab Invoices'),
                    'res_id': inv_id
                }
