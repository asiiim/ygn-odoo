# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'lab.request'
    
    text_after_result = fields.Html('Text After Result')
    text_before_result = fields.Html('Text Before Result')
