# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    vehicle_id = fields.Many2one('vehicle.vehicle', string="Vehicle", ondelete='restrict')
    seal_line_ids = fields.One2many('seal.line', 'invoice_id', string='Invoice Lines')

    @api.onchange('seal_line_ids')
    def onchange_seal_line(self):
        if self.seal_line_ids:
            master_seal_len = len(self.seal_line_ids.filtered(lambda r: r.seal_type.is_master == True))
            if master_seal_len > 1:
                raise UserError(_("You cannot have more than one master seal number."))
