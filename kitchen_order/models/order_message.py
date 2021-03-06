# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.osv import expression


class Message(models.Model):
    """ Model for case stages. This models the main stages of a kitchen order flow. 
    """
    _name = "kitchen.message"
    _description = "Message to include in product in Kitchen Order"
    _rec_name = 'name'
    _order = "name, id"

    name = fields.Char('Message', required=True, translate=True)
    code = fields.Char('Code')

    _sql_constraints = [
        ('code_key', 'unique (code)', 'This code is already assigned, please select other value!')
    ]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        messages = self.search(domain + args, limit=limit)
        return messages.name_get()

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for message in self:
            if not message.code:
                name = message.name
            else:
                name =  '[' + message.code + '] ' + message.name
            result.append((message.id, name))
        return result


