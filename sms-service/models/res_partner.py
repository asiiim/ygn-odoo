# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    messaging_list_ids = fields.Many2many('sms.messaging.list', 'group_partner_rel', 'messaging_list_ids', 'partner_ids', string="Messaging Lists")
