# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class FleetVehicle(models.Model):
    _name = 'fleet.vehicle'
    _inherit = ['fleet.vehicle', 'mail.activity.mixin']

    # partner_id = fields.Many2one(track_visibility='always')

    # @api.multi
    # def _track_subtype(self, init_values):
    #     self.ensure_one()
    #     if 'state' in init_values and self.state == 'cancel':
    #         return 'stock_inventory_chatter.mt_inventory_canceled'
    #     elif 'state' in init_values and self.state == 'confirm':
    #         return 'stock_inventory_chatter.mt_inventory_confirmed'
    #     elif 'state' in init_values and self.state == 'done':
    #         return 'stock_inventory_chatter.mt_inventory_done'
    #     return super(FleetVehicle, self)._track_subtype(init_values)
