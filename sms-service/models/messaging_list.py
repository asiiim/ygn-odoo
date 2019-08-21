# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class MessagingList(models.Model):
    _name = 'sms.messaging.list'

    name = fields.Char(string="Name", index=True)
    partner_ids = fields.Many2many('res.partner', 'group_partner_rel', 'partner_ids', 'messaging_list_ids', string="Partners")
    sms_multiple_id = fields.Many2many('sms.multiple', 'group_multi_sms_rel', 'sms_multiple_id', 'sms_messaging_list_ids', string="Multiple SMS")
