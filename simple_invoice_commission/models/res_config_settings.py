# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    commission_mode = fields.Selection([
        ('normal', 'Normal'),
        ('discount_deducted', 'Deducting Discount'),
    ], string='Commission Mode', default='normal')

    def get_commission_mode(self):
        params = self.env['ir.config_parameter'].sudo()
        return dict(
            commission_mode=params.get_param('commission_mode', default='normal')
        )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(self.get_commission_mode())
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('commission_mode', self[0].commission_mode or 'normal')
