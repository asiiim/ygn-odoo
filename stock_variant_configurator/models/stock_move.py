# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = ['stock.move', 'product.configurator']
    _name = 'stock.move'
    _description = 'Ygen Stock Move'

    product_tmpl_id = fields.Many2one(
        string='Product Template',
        comodel_name='product.template',
        auto_join=True, related=False)

    @api.depends('state', 'picking_id', 'product_id')
    def _compute_is_initial_demand_editable(self):
        for move in self:
            if self._context.get('planned_picking'):
                move.is_initial_demand_editable = True
            elif not move.picking_id.is_locked and move.state != 'done' and move.picking_id:
                move.is_initial_demand_editable = True
            elif move.product_id:
                move.is_initial_demand_editable = True
            else:
                move.is_initial_demand_editable = False
