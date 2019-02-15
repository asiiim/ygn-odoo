# -*- coding: utf-8 -*-

from odoo import models, fields, api

class District(models.Model):
    _name="res.country.district"

    name=fields.Char(string="Name")
    country_id = fields.Many2one('res.country', string="Country")
    state_ids = fields.Many2one('res.country.state', string="States")

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        if self.env.context.get('country_id'):
            args = args + [('country_id', '=', self.env.context.get('country_id'))]
        search_domain = [('name', operator, name)]
        records = self.search(search_domain + args, limit=limit)
        return [(record.id, record.display_name) for record in records]
