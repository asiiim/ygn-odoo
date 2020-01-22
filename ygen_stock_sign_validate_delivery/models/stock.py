# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import dateutil.parser
import logging

_logger = logging.getLogger(__name__)


class Picking(models.Model):
    _inherit = "stock.picking"

    user_id = fields.Many2one('res.users', string='Delivery Person', index=True, track_visibility='onchange')
    signature = fields.Binary('Delivery Signature', copy=False)
    is_sign_validate = fields.Boolean('Is Signed & Validated', default=False)
    is_scheduled = fields.Boolean('Is Scheduled?', default=False)

    # Schedule activity for the assigned user
    def schedule_delivery_activity(self):
        mail_act_obj = self.env['mail.activity']

        msg = "<b>Delivery Order Details</b><br/>"
        msg += "<li>Receiver Name: " + str(self.partner_id.name) + "<br/>"
        msg += "<li>Delivery Order No.: " + str(self.name) + "<br/>"
        msg += "<li>Contact Information: " + str(self.partner_id.mobile) + "<br/>"

        res_model_id = self.env.ref('stock.model_stock_picking').id
        res_id = self.env['stock.picking'].search([('name', '=', self.name)], limit=1).id
        activity_type = self.env['mail.activity.type'].search([('name', '=', 'Todo')], limit=1).id
        date = dateutil.parser.parse(self.scheduled_date).date()

        mail_vals = {
            'res_model_id': res_model_id,
            'res_id': res_id,
            'activity_type_id': activity_type,
            'summary': 'To Do Delivery of ' + str(self.name),
            'date_deadline': date,
            'user_id': self.user_id.id,
            'note': msg
        }
        mail = mail_act_obj.create(mail_vals)
        self.write({'is_scheduled': True})
        return mail

    # Override validate method
    @api.multi
    def button_validate(self):
        if self.state in ["confirmed", "assigned"]:
            for moveline in self.move_lines:
                if moveline.product_uom_qty:
                    moveline.quantity_done = moveline.product_uom_qty
            super(Picking, self).button_validate()

    # Sign and Validate Delivery
    @api.multi
    def button_sign_validate(self):
        """Return action to sign and validate the delivery"""
        stock_sign_validate_view_id = self.env.ref('ygen_stock_sign_validate_delivery.stock_sign_validate_view').id

        return {
            'name': _('Sign and Validate Delivery'),
            'res_model': 'stock.picking',
            'res_id': self.id,
            'views': [(stock_sign_validate_view_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new'
        }
    
    def sign(self):
        stock_pick_obj = self.env['stock.picking']
        stkpk = stock_pick_obj.browse(self._context.get('active_id'))
        stkpk.write({'signature': self.signature})

    def sign_validate(self):
        stock_pick_obj = self.env['stock.picking']
        stkpk = stock_pick_obj.browse(self._context.get('active_id'))

        if stkpk.state not in ["done", "cancel"]:
            stkpk.button_validate()
        
        stkpk.write({
            'signature': self.signature,
            'is_sign_validate': True
        })
