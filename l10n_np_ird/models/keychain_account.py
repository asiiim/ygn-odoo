# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

import logging
import json

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class IRDAccount(models.Model):
    _inherit = 'keychain.account'

    namespace = fields.Selection(
        selection_add=[('ird_account', 'IRD')])

    def _ird_account_init_data(self):
        return {
            "url": "http://103.1.92.174:9050/"
        }

    def _ird_account_validate_data(self, data):
        return True
