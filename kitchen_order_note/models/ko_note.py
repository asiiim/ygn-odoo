# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.osv import expression


class KitchenOrderNotes(models.Model):
    _name = "kitchen.order.notes"
    _description = 'Kitchen Order Notes'
    _rec_name = 'name'
    _order = "sequence, name, id"
    
    sequence = fields.Integer(string="Sequence")
    name = fields.Char(string="Note")
    code = fields.Char('Code')

    _sql_constraints = [
        ('code_key', 'unique (code)', 'This code is already assigned, please select other value!')
    ]

    @api.model
    def default_get(self, default_fields):
        default_name = self._context.get('default_name')
        contextual_self = self.with_context(default_name=default_name)
        return super(KitchenOrderNotes, contextual_self).default_get(default_fields)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        notes = self.search(domain + args, limit=limit)
        return notes.name_get()

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for note in self:
            if not note.code:
                name = note.name
            else:
                name =  '[' + note.code + '] ' + note.name
            result.append((note.id, name))
        return result
