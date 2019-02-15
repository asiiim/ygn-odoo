# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    vat = fields.Char(string='PAN', help="Tax Identification Number.Fill it if the company is subjected to taxes. Used by the some of the legal statements.")
    district_id = fields.Many2one('res.country.district', string="District")
    l10n_np_state_ids = fields.Many2one(related='district_id.state_ids', string="States")
