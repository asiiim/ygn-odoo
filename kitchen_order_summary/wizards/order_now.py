# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, api, _
from odoo.exceptions import Warning, ValidationError, UserError

from odoo.addons import decimal_precision as dp

import logging

_logger = logging.getLogger(__name__)


class ProductConfiguratorSaleOrderKO(models.TransientModel):
    _inherit = 'product.configurator.ordernow.ko'

    custom_image = fields.Binary(
        "Custom Image", attachment=True,
        help="This field holds the custom image for the kitchen order.")

    secondary_custom_image = fields.Binary(
        "Secondary Custom Image", attachment=True,
        help="This field holds the secondary custom image for the kitchen order.")

    @api.multi
    def _prepare_kitchen_order(self):
        ko_vals = super(ProductConfiguratorSaleOrderKO, self)._prepare_kitchen_order()

        ko_vals.update({
            'custom_image': self.custom_image,
            'secondary_custom_image': self.secondary_custom_image
        })

        return ko_vals