# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID, _


class Partner(models.Model):
    _inherit = 'res.partner'
    
    # vat = fields.Char(string='PAN', help="Tax Identification Number.Fill it if the company is subjected to taxes. Used by the some of the legal statements.")
    district_id = fields.Many2one('res.country.district', string="District", ondelete='restrict')
    
    # Why do we need this?
    # l10n_np_state_ids = fields.Many2one(related='district_id.state_ids', string="States")

    # @ovverride probably we have to override
    # _display_address() method to get the result
    # bcz it is no way possible by other way
    # @api.model
    # def _address_fields(self):
    #     """Returns the list of address fields that are synced from the parent."""
    #     address_fields_tmp = super(Partner, self)._address_fields()

    #     # Inject district_id into the list
    #     address_fields_tmp.insert(address_fields_tmp.index('country_id'), 'district_id')
    #     return address_fields_tmp

    # @api.multi
    # def _display_address(self, without_company=False):
    #     tmp_display_format = super(Partner, self)._display_address(without_company)
    #     print(tmp_display_format)
    #     return tmp_display_format
