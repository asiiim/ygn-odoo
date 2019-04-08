# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    # Do not override this field. 
    # Instead use country_id.vat_label
    # for more flexibility
    # vat = fields.Char(related='partner_id.vat', string="PAN")

    # Add selection field for external report layout
    external_report_layout = fields.Selection(selection_add=[('boxed2', 'Boxed Black')])

    # This is not the way to inject district_id
    # district_id = fields.Many2one('res.country.district', string="District")
    district_id = fields.Many2one('res.country.district', compute='_compute_address', inverse='_inverse_district', string="District")
    
    # This is a wrong one
    # l10n_np_state_ids = fields.Many2one(related='district_id.state_ids', string="States")
    # state_ids = fields.Many2one(related='country_id.state_ids', string="States")

    def _get_company_address_fields(self, partner):
        address = super(Company, self)._get_company_address_fields(partner)
        address.update({'district_id' : partner.district_id})
        return address

    def _inverse_district(self):
        for company in self:
            company.partner_id.district_id = company.district_id