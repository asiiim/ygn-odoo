# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CountryDistrict(models.Model):
    _name="res.country.district"
    _description = 'District'
    _order = 'name'

    name=fields.Char(string="Name")
    country_id = fields.Many2one('res.country', string="Country")
    state_id = fields.Many2one('res.country.state', string="State")

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        if self.env.context.get('country_id'):
            args = args + [('country_id', '=', self.env.context.get('country_id'))]
        search_domain = [('name', operator, name)]
        records = self.search(search_domain + args, limit=limit)
        return [(record.id, record.display_name) for record in records]


class CountryState(models.Model):
    _inherit = 'res.country.state'

    district_ids = fields.One2many('res.country.district', 'state_id', string='Districts')


class Country(models.Model):
    _inherit = 'res.country'

    district_ids = fields.One2many('res.country.district', 'country_id', string='Districts')
