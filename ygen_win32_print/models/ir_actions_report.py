# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

import cgi
import os
import tempfile
import win32api
import win32print
import errno
import time
import logging
import tempfile

from odoo.tools.config import config
from odoo import api, exceptions, fields, models, _
from contextlib import closing

_logger = logging.getLogger(__name__)

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    direct_print = fields.Boolean(string='Direct Print', copy=False, default=False)
    printer_id = fields.Many2one('ygen.printer', string='Select Printer', )

    def _direct_report_print(self, data):
        # create a temporary file with path
        fd, filepath = tempfile.mkstemp(".pdf", "ygen_")
        
        # write the report content on the created temporary file
        fo = os.fdopen(fd, "wb")
        fo.write(data)
        fo.close()
        # close the file
        try:
            os.close(fd)
        except OSError as oserr:
            if oserr.args[0] == errno.EBADF:
                _logger.error("Closing file has closed file descriptor.")
            else:
                _logger.error("Some other error: %s" % (oserr))
        else:
            _logger.error("File descriptor not closed.")

        # Get paths for silent printing tools from config
        GHOSTSCRIPT_PATH = config.get("ghostscript_path")
        GSPRINT_PATH = config.get("gsprint_path")
        # command for direct print
        # printer = win32print.GetDefaultPrinter()
        # win32api.ShellExecute(0, "print", filepath, '"%s"' % printer, ".", 0)
        printer = self.printer_id.name if self.printer_id else str(win32print.GetDefaultPrinter())
        win32api.ShellExecute(0, 'open', GSPRINT_PATH, '-ghostscript "'+GHOSTSCRIPT_PATH+'" -printer "'+printer+'" "'+filepath+'"', '.', 0)

    @api.noguess
    def report_action(self, docids, data=None, config=True):
        report_act = super(IrActionsReport, self).report_action(docids, data, config)

        if self.direct_print:
            data, dataformat = self.render_qweb_pdf(report_act.get('context')['active_ids'], report_act.get('data'))
            self._direct_report_print(data)
            return
        else:
            return report_act
