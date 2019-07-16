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
    weight = fields.Float('Readymade Weight')
    loss = fields.Float('Jarti [Loss]')
    wage = fields.Float('Jyala [Wage]')
    gems_cost = fields.Float('Patthar [Gems] Cost')
    base_product_id = fields.Many2one('product.template', string='Base Products', domain="[('is_base','=',True)]")

    # Compute sales price if the products depend the base product
    @api.onchange('weight', 'loss', 'wage', 'gems_cost')
    def compute_sales_price(self):
        for product in self:
            if product.can_depend_base:
                product.list_price = ((product.weight + product.loss) * product.base_product_id.list_price) + product.wage + product.gems_cost
    
    # Compute sales price of the products when changing the price of the base product
    @api.onchange('list_price')
    def adjust_sales_price(self):
        if self.is_base:
            base_rate = self.list_price
            dependent_products = self.env['product.template'].search([('base_product_id', '=', self.id)])
            
            for product in dependent_products:
                product.list_price = ((product.weight + product.loss) * base_rate) + product.wage + product.gems_cost

    @api.multi
    def write(self, values):
        total_cost = 0.0
        product_templ = super(ProductTemplate, self).write(values)
        if self.is_base:
            base_rate = self.list_price
            dependent_products = self.env['product.template'].search([('base_product_id', '=', self.id)])
            
            for product in dependent_products:
                total_cost = ((product.weight + product.loss) * base_rate) + product.wage + product.gems_cost
                product.write({
                    'list_price': total_cost
                })
        return product_templ

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


                