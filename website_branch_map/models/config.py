# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Config(models.TransientModel):
    _name = 'branch.map.config'

    @api.model
    def get_api_key(self):
        return self.env['ir.config_parameter'].sudo().get_param('google_maps_api_key')
