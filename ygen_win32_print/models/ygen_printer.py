# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import ValidationError, AccessError, UserError
from odoo.modules.module import get_module_resource

import os
import sys
import win32print

import cgi
import tempfile
import win32api

import pywintypes

import logging

_logger = logging.getLogger(__name__)


class YgenPrinter(models.Model):
    _name = "ygen.printer"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "This printer are accessed directly to print the file."
    _order = "sequence, id"

    name = fields.Char(string="Name", required=True, copy=False,
                       index=True, track_visibility='onchange')
    sequence = fields.Integer(
        help='Printer Sequence', track_visibility='onchange')
    description = fields.Text(
        string="Description", track_visibility='onchange')
    default_printer = fields.Boolean(string='Set Default', default=False, copy=False)

    @api.model
    def create(self, values):
        if values.get('name'):
            printer_name = values.get('name')
            try:
                # check if printer exists in the windows system
                printer = win32print.OpenPrinter(printer_name)
                win32print.ClosePrinter(printer)
            except pywintypes.error:
                raise UserError(
                    _('The printer name you have entered is not correct.\n Check the name in the Control Panel >> Printer Settings'))

        # check if the printer is set to default 
        if values.get('default_printer'):
            win32print.SetDefaultPrinter(values.get('name'))
            for printer in self.env['ygen.printer'].search([]):
                printer.write({'default_printer': False})
            
        return super(YgenPrinter, self).create(values)

    @api.multi
    def write(self, values):
        if values.get('name'):
            printer_name = values.get('name')
            try:
                # check if printer exists in the windows system
                printer = win32print.OpenPrinter(printer_name)
                win32print.ClosePrinter(printer)
            except pywintypes.error:
                raise UserError(
                    _('The printer name you have entered is not correct.\n Check the name in the Control Panel >> Printer Settings'))
        
        # check if the printer is set to default    
        if values.get('default_printer'):
            win32print.SetDefaultPrinter(self.name)
            for printer in self.env['ygen.printer'].search([]):
                _logger.warning("Printer:::: " + str(printer))
                printer.write({'default_printer': False})
        return super(YgenPrinter, self).write(values)
