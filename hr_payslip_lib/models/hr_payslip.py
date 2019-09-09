# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

import time
import math

from datetime import datetime
from datetime import time as datetime_time
from dateutil import relativedelta

import babel

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    payslip_days = fields.Float('Payslip Days', compute="_compute_payslip_days", store=True)

    @api.depends('date_from', 'date_to')
    def _compute_payslip_days(self):
        """Return return the number of the payslip days."""
        for slip in self:
            _logger.warning('Date from: ' + str(slip.date_from))
            _logger.warning('Date to: ' + str(slip.date_to))
            if slip.date_from and slip.date_to:
                
                from_dt = fields.Datetime.from_string(slip.date_from)
                to_dt = fields.Datetime.from_string(slip.date_to)

                time_delta = to_dt - from_dt
                _logger.warning('Time Delta: ' + str(time_delta))
                slip.payslip_days = math.ceil(time_delta.days + float(time_delta.seconds) / 86400) + 1.0
