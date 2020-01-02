# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.osv import expression

class ResPartner(models.Model):
    """Overrride name_search, name_get and default_get"""
    _inherit = "res.partner"

    @api.model
    def default_get(self, default_fields):
        default_name = self._context.get('default_name')
        default_mobile = self._context.get('default_mobile')
        if default_name and not default_mobile:
            try:
                default_mobile = int(default_name)
            except ValueError:
                pass
            if default_mobile:
                default_name = default_mobile
        contextual_self = self.with_context(default_name=default_name, default_mobile=default_mobile)
        return super(ResPartner, contextual_self).default_get(default_fields)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', '|', ('ref', operator, name), ('mobile', operator, name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        self.search(domain + args, limit=limit)
        # return partners.name_get()
        return super(ResPartner, self).name_search(name, args, operator=operator, limit=limit)

    @api.multi
    @api.depends('name', 'mobile')
    def name_get(self):
        result = []
        for partner in self:
            if not partner.mobile:
                name = partner.name
            else:
                name =  partner.name + ' [ ' + partner.mobile + ' ]'
            result.append((partner.id, name))
        return result