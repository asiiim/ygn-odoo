# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class UpdateProductCost(models.TransientModel):
    _name = 'update.product.cost'
    _description = 'Update Product Standard Price in Manufacturing Order'

    # TDE FIXME: add production_id field
    mo_id = fields.Many2one('mrp.production', 'Manufacturing Order', required=True)
    standard_price = fields.Float(
        'Cost Price', company_dependent=True,
        digits=dp.get_precision('Product Price'),
        groups="base.group_user",
        help = "Cost used for stock valuation in standard price and as a first price to set in average/fifo. "
               "Also used as a base price for pricelists. "
               "Expressed in the default unit of measure of the product.")
    lst_price = fields.Float(related='mo_id.product_id.lst_price', string='Sale Price')

    @api.model
    def default_get(self, fields):
        res = super(UpdateProductCost, self).default_get(fields)
        if 'mo_id' in fields and not res.get('mo_id') and self._context.get('active_model') == 'mrp.production' and self._context.get('active_id'):
            res['mo_id'] = self._context['active_id']
        if 'standard_price' in fields and not res.get('standard_price') and res.get('mo_id'):
            res['standard_price'] = self.env['mrp.production'].browse(res['mo_id']).product_id.standard_price
        return res

    @api.multi
    def update_product_cost(self):
        for wizard in self:
            production = wizard.mo_id
            product = self.env['product.product'].search([('id', '=', production.product_id.id)])
            product.write({
                'standard_price': wizard.standard_price
            })
        return {}