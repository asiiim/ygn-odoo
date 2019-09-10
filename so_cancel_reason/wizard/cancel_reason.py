# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api


class SOCancel(models.TransientModel):

    """ Ask a reason for the sale order cancellation."""
    _name = 'so.cancel'
    _description = __doc__

    # The name of module has been given so.cancel as oca has 
    # already taken the trivial name and theri module is not 
    # present for version 11.0
    reason_id = fields.Many2one(
        'so.cancel.reason',
        string='Reason',
        required=True)

    @api.multi
    def confirm_cancel(self):
        self.ensure_one()
        act_close = {'type': 'ir.actions.act_window_close'}
        sale_ids = self._context.get('active_ids')
        if sale_ids is None:
            return act_close
        assert len(sale_ids) == 1, "Only 1 sale ID expected"
        sale = self.env['sale.order'].browse(sale_ids)
        sale.cancel_reason_id = self.reason_id.id
        sale.action_cancel()
        return act_close
