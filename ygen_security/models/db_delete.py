# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

import time
import psycopg2
import random
import string

import odoo
import datetime
from odoo.service import db
from odoo.tools.translate import _
from odoo import api, models, fields, SUPERUSER_ID, exceptions
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

import logging
_logger = logging.getLogger(__name__)


class DbDelete(models.Model):
    _name = 'db.delete'

    @api.model
    def _cron_delete_expired_databases(self):

        db_exp_datetime = self.env['ir.config_parameter'].sudo().get_param('db_expiration_datetime')

        if datetime.datetime.now() >= fields.Datetime().from_string(db_exp_datetime):
            self.delete_database()

    def delete_database(self):
        db.exp_drop(self.env.cr.dbname)
