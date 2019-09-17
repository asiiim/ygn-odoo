# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Message(models.Model):
    """ Model for case stages. This models the main stages of a kitchen order flow. 
    """
    _name = "kitchen.message"
    _description = "Message to include in product in Kitchen Order"
    _rec_name = 'name'
    _order = "name, id"

    name = fields.Char('Message', required=True, translate=True)
