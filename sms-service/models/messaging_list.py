# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class MessagingList(models.Model):
    _name = 'sms.messaging.list'
    _description = "Create a group of receivers to send multiple SMS."

    name = fields.Char(string="Name", index=True, track_visibility='onchange')
    partner_ids = fields.Many2many('res.partner', 'group_partner_rel', 'partner_ids', 'messaging_list_ids', string="Recipients", track_visibility='onchange')
    sms_multiple_id = fields.Many2many('sms.multiple', 'group_multi_sms_rel', 'sms_multiple_id', 'sms_messaging_list_ids', string="Multiple SMS", track_visibility='onchange')
