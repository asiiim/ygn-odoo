# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def action_zoom_product(self):
        """
        Zooms the current product showing image_medium field.
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'name': self.name,
            'res_id': self.id,
            # 'view_mode': 'form',
            # 'view_id': product_tmpl_zoom_view_id,
            'views': [(self.env.ref('product_template_zoom.product_tmpl_zoom_view').id, 'form')],
            'target': 'new',
            'context': dict(
                self.env.context,
            ),
        }