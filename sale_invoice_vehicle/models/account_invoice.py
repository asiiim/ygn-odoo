# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    vehicle_id = fields.Many2one('vehicle.vehicle', string="Vehicle", ondelete='restrict')
    seal_line_ids = fields.One2many('seal.line', 'invoice_id', string='Invoice Lines')
