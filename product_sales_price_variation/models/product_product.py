# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

import logging

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = "product.product"

    is_base = fields.Boolean('Is Base Product', related='product_tmpl_id.is_base')
    can_depend_base = fields.Boolean('Is Dependent Product', related='product_tmpl_id.can_depend_base')
    ready_weight = fields.Float('Readymade Weight')
    weight_uom_id = fields.Many2one(related='product_tmpl_id.weight_uom_id', string='Weight Unit')
    loss = fields.Float('Jarti [Loss]')
    wage = fields.Float('Jyala [Wage]')
    gems_cost = fields.Float('Patthar [Gems] Cost')
    base_product_id = fields.Many2one('product.product', string='Base Products', domain="[('is_base','=',True)]")

    # Compute sales price if the products depend the base product
    @api.onchange('ready_weight', 'loss', 'wage', 'gems_cost', 'base_product_id', 'weight_uom_id')
    def compute_sales_price(self):
        for product in self:
            if product.can_depend_base and product.base_product_id:
                if product.weight_uom_id != product.base_product_id.product_tmpl_id.uom_id:
                    raise UserError(_('The unit of measurement of this product is not same with the base product !\nMake sure it is same and then proceed.'))
                product.fix_price = ((product.ready_weight + product.loss) * product.base_product_id.list_price) + product.wage + product.gems_cost
    
    # Change all the dependent products' sales price when the sales price of the base product is changed
    @api.multi
    def write(self, values):
        total_cost = 0.0
        for variant in self:
            product_write = super(ProductProduct, variant).write(values)
            if variant.is_base:
                base_rate = variant.list_price
                dependent_products = self.env['product.product'].search([('base_product_id', '=', variant.id), ('can_depend_base', '=', True)])
                
                for product in dependent_products:
                    total_cost = ((product.ready_weight + product.loss) * base_rate) + product.wage + product.gems_cost
                    product.write({
                        'fix_price': total_cost
                    })
        # return product_write

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
            if product.product_tmpl_id.is_base:
                dependent_products = self.env['product.product'].search([('base_product_id', '=', product.id), ('can_depend_base', '=', True)])
                if dependent_products:
                    raise UserError(_('You can not delete a base product which is being depended by other products! \nTry to delete the dependent products first.'))
        return super(ProductProduct, self).unlink()

            


                