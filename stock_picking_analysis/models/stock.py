# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

import time
import math

from datetime import datetime
from datetime import time as datetime_time
from dateutil import relativedelta

from odoo import api, fields, models, _
import dateutil.parser
import logging

_logger = logging.getLogger(__name__)


class Picking(models.Model):
    _inherit = "stock.picking"

    delivery_delay = fields.Float('Delivery Delay', default=0, copy=False, readonly=True, track_visibility='onchange')
    delivery_process_time = fields.Float('Process Time', default=0, copy=False, readonly=True, track_visibility='onchange')

    @api.multi
    def button_validate(self):
        self.ensure_one()
        # Call super to get done date
        validate = super(Picking, self).button_validate()

        # Calculate delivery delay and delivery process time
        date_done = fields.Datetime.from_string(self.date_done)
        delivery_created = fields.Datetime.from_string(self.create_date)
        delivery_scheduled = fields.Datetime.from_string(self.scheduled_date)

        delv_delay = date_done - delivery_scheduled
        delv_processed = date_done - delivery_created

        delv_delay_hrs = 0.0
        delv_processed_hrs = 0.0

        # Get float values of the time intervals into hrs and minutes
        if delv_delay.days >= 0:
            delv_delay_hrs = delv_delay.seconds / 3600
        else:
            delv_delay_hrs = 0.0

        delv_processed_hrs = delv_processed.seconds / 3600

        # Write Delivery Date, Delay and Process time
        self.write({
            'delivery_delay': delv_delay_hrs,
            'delivery_process_time': delv_processed_hrs
        })

        return validate
