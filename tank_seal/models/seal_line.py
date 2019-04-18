# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class SealLine(models.Model):
    _name = 'seal.line'
    _order = "sequence, name"

    name = fields.Integer("Seal Number", required=True)
    seal_type = fields.Many2one("seal.type", string="Seal Type", required=True)
    chamber_id = fields.Many2one("chamber.chamber", string="Chamber Number")
    sequence = fields.Integer("Sequence")
    invoice_id = fields.Many2one('account.invoice', string='Invoice Reference', ondelete='cascade', index=True)
    is_master = fields.Boolean(related='seal_type.is_master', string="Master Seal?")

    # _sql_constraints = [
    #     ('unique_seal_number', 'UNIQUE(seal_type, chamber_id, invoice_id, name)', 'You can have only one seal number with same seal type and chamber number.'),
    # ]