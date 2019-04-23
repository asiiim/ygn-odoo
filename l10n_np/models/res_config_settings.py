# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    module_l10n_np_ird = fields.Boolean("Sync with IRD")
    
    @api.multi
    def edit_external_header(self):
        if self.external_report_layout in ["boxed2"]:
            return self._prepare_report_view_action('l10n_np.external_layout_' + self.external_report_layout)
        return super(ResConfigSettings, self).edit_external_header()
