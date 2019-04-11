# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_max_shrinkage_loss = fields.Boolean(string="Maximum Shrinkage Loss", help="Check this option if you want to perform the inventory adjustment only incase of maximum shrinkage loss.", default=False)

    max_shrinkage_loss = fields.Float(related="company_id.max_shrinkage_loss", string="Maximum Shrikage Loss(in litres)")

    @api.onchange('use_max_shrinkage_loss')
    def _onchange_use_max_shrinkage_loss(self):
        if not self.use_max_shrinkage_loss:
            self.max_shrinkage_loss = 0.0

    @api.multi
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            use_max_shrinkage_loss=self.env['ir.config_parameter'].sudo().get_param('station.use_max_shrinkage_loss')
        )
        _logger.warning("AAAFTER RES CONFIG VALUES ----------------- " + str(res))
        _logger.warning("RES PARAM GET ----------------- " + str(self.env['ir.config_parameter'].sudo().get_param('station.max_shrinkage_loss')))
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('station.use_max_shrinkage_loss', self.use_max_shrinkage_loss)
        # self.env['ir.config_parameter'].sudo().set_param('station.max_shrinkage_loss', self.max_shrinkage_loss)
