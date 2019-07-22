# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
import datetime
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SignatureTemplate(models.Model):
    _name = 'signature.name'
    
    name = fields.Char(string='Name')
    signature = fields.Html('Signature')
    
    