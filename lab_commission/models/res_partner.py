# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
import logging
import datetime
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class LabCommision(models.Model):
    _inherit = 'res.partner'
    
    commission= fields.Float(string='Lab Commision')
    