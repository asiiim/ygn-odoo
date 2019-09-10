# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    cancel_reason_id = fields.Many2one(
        'so.cancel.reason',
        string="Reason for cancellation",
        readonly=True,
        ondelete="restrict")


class SOCancelReason(models.Model):
    _name = 'so.cancel.reason'
    _description = 'Sale Order Cancel Reason'

    # The name of module has been given so.cancel as oca has 
    # already taken the trivial name and theri module is not 
    # present for version 11.0
    name = fields.Char('Reason', required=True, translate=True)
