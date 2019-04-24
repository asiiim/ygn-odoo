# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ird_api_uri = fields.Char(string='Ird URI', help="The URI used for API calls")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            ird_api_uri=self.env['ir.config_parameter'].sudo().get_param('ird_api_uri'),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('ird_api_uri', self.ird_api_uri)
