# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_base = fields.Boolean('Is Base Product', default=False)
    can_depend_base = fields.Boolean('Can depend the Base Product', default=False)

    # Set dependent product boolean to false if base product changed to true
    @api.onchange('is_base')
    def toggle_dependent_product(self):
        for product in self:
            if product.is_base:
                product.can_depend_base = False

    # Prevent deleting base product if it is linked with dependent products
    @api.multi
    def unlink(self):
        for product in self:
            if product.is_base and product.product_variant_id:
                dependent_products = self.env['product.product'].search([('base_product_id', '=', product.product_variant_id.id), ('can_depend_base', '=', True)])
                if dependent_products:
                    raise UserError(_('You can not delete a base product which is being depended by other products! \nTry to delete the dependent products first.'))
        return super(ProductTemplate, self).unlink()


                