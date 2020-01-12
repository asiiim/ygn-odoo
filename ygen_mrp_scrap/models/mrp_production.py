# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import Warning, ValidationError, UserError
from odoo.tools import float_is_zero
import math

import logging

_logger = logging.getLogger(__name__)

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def _update_product_to_produce(self, production, qty):
        production_move = production.move_finished_ids.filtered(lambda x:x.product_id.id == production.product_id.id and x.state not in ('done', 'cancel'))
        if production_move:
            production_move.write({'product_uom_qty': qty})
        else:
            production_move = production._generate_finished_moves()
            production_move = production.move_finished_ids.filtered(lambda x : x.state not in ('done', 'cancel') and production.product_id.id == x.product_id.id)
            production_move.write({'product_uom_qty': qty})


    @api.multi
    def update_finished_product_qty(self, qty):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        
        for rec in self:
            rec.write({'product_qty': qty})
            done_moves = rec.move_finished_ids.filtered(lambda x: x.state == 'done' and x.product_id == rec.product_id)
            qty_produced = rec.product_id.uom_id._compute_quantity(sum(done_moves.mapped('product_qty')), rec.product_uom_id)
            factor = rec.product_uom_id._compute_quantity(qty - qty_produced, rec.bom_id.product_uom_id) / rec.bom_id.product_qty
            boms, lines = rec.bom_id.explode(rec.product_id, factor, picking_type=rec.bom_id.picking_type_id)
            
            for line, line_data in lines:
                rec._update_raw_move(line, line_data)
            
            operation_bom_qty = {}
            for bom, bom_data in boms:
                for operation in bom.routing_id.operation_ids:
                    operation_bom_qty[operation.id] = bom_data['qty']
            
            self._update_product_to_produce(rec, qty - qty_produced)
            moves = rec.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            moves._action_assign()
            
            for wo in rec.workorder_ids:
                operation = wo.operation_id
                
                if operation_bom_qty.get(operation.id):
                    cycle_number = math.ceil(operation_bom_qty[operation.id] / operation.workcenter_id.capacity)
                    wo.duration_expected = (operation.workcenter_id.time_start +
                                 operation.workcenter_id.time_stop +
                                 cycle_number * operation.time_cycle * 100.0 / operation.workcenter_id.time_efficiency)
                quantity = wo.qty_production - wo.qty_produced
                
                if rec.product_id.tracking == 'serial':
                    quantity = 1.0 if not float_is_zero(quantity, precision_digits=precision) else 0.0
                else:
                    quantity = quantity if (quantity > 0) else 0
                
                if float_is_zero(quantity, precision_digits=precision):
                    wo.final_lot_id = False
                    wo.active_move_line_ids.unlink()
                
                wo.qty_producing = quantity
                if wo.qty_produced < wo.qty_production and wo.state == 'done':
                    wo.state = 'progress'
                if wo.qty_produced == wo.qty_production and wo.state == 'progress':
                    wo.state = 'done'
                
                moves_raw = rec.move_raw_ids.filtered(lambda move: move.operation_id == operation and move.state not in ('done', 'cancel'))
                if wo == rec.workorder_ids[-1]:
                    moves_raw |= rec.move_raw_ids.filtered(lambda move: not move.operation_id)
                moves_finished = rec.move_finished_ids.filtered(lambda move: move.operation_id == operation)
                moves_raw.mapped('move_line_ids').write({'workorder_id': wo.id})
                (moves_finished + moves_raw).write({'workorder_id': wo.id})
                
                if quantity > 0 and wo.move_raw_ids.filtered(lambda x: x.product_id.tracking != 'none') and not wo.active_move_line_ids:
                    wo._generate_lot_ids()
        return {}