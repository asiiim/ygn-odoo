# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCountry(models.Model):
    _inherit = 'res.company'

    # Do not override this field. 
    # Instead use country_id.vat_label
    # for more flexibility
    # vat = fields.Char(related='partner_id.vat', string="PAN")

    # Add selection field for external report layout
    external_report_layout = fields.Selection(selection_add=[('boxed2', 'Boxed Black')]) 
    district_id = fields.Many2one('res.country.district', string="District")
    l10n_np_state_ids = fields.Many2one(related='district_id.state_ids', string="States")
    # state_ids = fields.Many2one(related='country_id.state_ids', string="States")