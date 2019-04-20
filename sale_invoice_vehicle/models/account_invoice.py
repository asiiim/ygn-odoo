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
    seal_line_ids = fields.One2many('seal.line', 'invoice_id', string='Invoice Lines', copy=True)

    @api.onchange('seal_line_ids')
    def onchange_seal_line(self):
        if self.seal_line_ids:
            master_seal_len = len(self.seal_line_ids.filtered(lambda r: r.seal_type.is_master == True))
            if master_seal_len > 1:
                raise UserError(_("You cannot have more than one master seal number."))

    @api.model
    def create(self, vals):

        if vals.get('seal_line_ids'):

            chamber_list = []

            upseals = 0
            downseals = 0
            master = 0

            for seal_line in vals['seal_line_ids']:
                for seal in range(len(seal_line)):
                    if seal == 2:
                        
                        if 'chamber_id' in seal_line[seal]:
                            chamber_list.append(self.env['chamber.chamber'].browse(seal_line[seal]['chamber_id']).name)
                        
                        seal_types = self.env['seal.type'].browse(seal_line[seal]['seal_type'])
                        if seal_types.name == 'Up Seal':
                            upseals += 1
                        elif seal_types.name == 'Down Seal':
                            downseals += 1
                        elif seal_types.name == 'Master Seal':
                            master += 1

            chambers = len(list(dict.fromkeys(chamber_list)))


            if upseals != chambers:
                raise UserError(_("Missing Up Seal Number for some Chambers."))
            
            if downseals != chambers:
                raise UserError(_("Missing Down Seal Number for some Chambers."))

            if master == 0:
                raise UserError(_("Missing Master Seal Number."))

        return super(AccountInvoice, self).create(vals)
    
    @api.multi
    def write(self, vals):
        
        res = super(AccountInvoice, self).write(vals)

        if self.seal_line_ids:
            
            up_seal_line_size = len(self.seal_line_ids.filtered(lambda r: r.seal_type.name == "Up Seal"))
            down_seal_line_size = len(self.seal_line_ids.filtered(lambda r: r.seal_type.name == "Down Seal"))
            
            res = []
            for seal_line in self.seal_line_ids.filtered(lambda r: r.chamber_id):
                res.append(seal_line.chamber_id.name)
            chamber_size = len(list(dict.fromkeys(res)))

            if up_seal_line_size != chamber_size:
                raise UserError(_("Missing Up Seal Number for some Chambers."))
            
            if down_seal_line_size != chamber_size:
                raise UserError(_("Missing Down Seal Number for some Chambers."))

            if not self.seal_line_ids.filtered(lambda r: r.seal_type.name == "Master Seal"):
                raise UserError(_("Missing Master Seal Number."))

        return res
