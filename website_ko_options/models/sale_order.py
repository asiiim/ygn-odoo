# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

import pytz

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    ko_message = fields.Char(string="Message", track_visibility='onchange')
    ko_note = fields.Text(string="Kitchen Order Note", translate=True, track_visibility='onchange')

    @api.multi
    def _cart_update_ko(self, ko_message="", ko_note="", delivery_date=None, **kwargs):
        self.ensure_one()
        # dt = fields.Datetime.from_string(delivery_date)

        self.write({
            'ko_message': ko_message,
            'ko_note': ko_note,
            'requested_date': delivery_date,
        })
