# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    lead_time = fields.Float(string='Lead Time (In Hours)', help="Lead time difference between client requested datetime and datetime to finish the order in the kitchen.")

    def get_lead_time(self):
        params = self.env['ir.config_parameter'].sudo()
        return dict(lead_time=float(params.get_param('lead_time', default=0.0)))

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(self.get_lead_time())
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('lead_time', self[0].lead_time or 0.0)
