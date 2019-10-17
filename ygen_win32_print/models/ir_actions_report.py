# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

import cgi
import os
import sys
import tempfile
import win32api
import win32print
import errno
import time
import logging
import tempfile

from odoo.tools.config import config
from odoo import api, exceptions, fields, models, _
from odoo.exceptions import UserError
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
        # fo = os.fdopen(fd, "wb")
        # fo.write(data)
        # fo.close()
        try:
            os.write(fd, data)
        finally:
            os.close(fd)
        # close the file
        # try:
        #     os.close(fd)
        # except OSError as oserr:
        #     if oserr.args[0] == errno.EBADF:
        #         _logger.error("Closing file has closed file descriptor.")
        #     else:
        #         _logger.error("Some other error: %s" % (oserr))
        # else:
        #     _logger.error("File descriptor not closed.")

        # Get paths for silent printing tools from config
        GHOSTSCRIPT_PATH = config.get("ghostscript_path")
        GSPRINT_PATH = config.get("gsprint_path")
        # command for direct print
        # printer = win32print.GetDefaultPrinter()
        # win32api.ShellExecute(0, "print", filepath, '"%s"' % printer, ".", 0)

        _logger.info("Printing: '%s'" % (filepath))
        printer = self.printer_id.name if self.printer_id else str(win32print.GetDefaultPrinter())
        
        # printer = "Microsoft XPS Document Writer"
        # args = '"' + GHOSTSCRIPT_PATH + '" -sDEVICE=mswinpr2 -dBatch -dNOPAUSE -dFitPage -sOutputFile="%printer%'+printer+'" "'+filepath+'"'
        command = GSPRINT_PATH + ' -ghostscript "' + GHOSTSCRIPT_PATH + '" -printer "'+printer+'" "'+filepath+'"'
        # result = win32api.ShellExecute(0, 'open', GSPRINT_PATH, '-ghostscript "'+GHOSTSCRIPT_PATH+'" -printer "'+printer+'" "'+filepath+'"', '.', 0)
        self.execute_command(command)
        return True
        # subprocess.call(args, shell=True)
        # _logger.warning(result)

    def execute_command(self, command):
        """
        Execute external program
        @param command is a list of strings
        """
        #code from https://www.odoo.com/it_IT/forum/help-1/question/49495

        _logger.info("Going to execute: " + str(command))

        #wrt subprocess, subprocess32 allows to set a timeout
        from subprocess32 import check_output, CalledProcessError, TimeoutExpired, STDOUT
        try:
            import subprocess32
            check_output(command, stderr=STDOUT, timeout=60)	#may raise CalledProcessError,TimeoutExpired
            _logger.info("Command successfully terminated with exit code 0. ")
        except CalledProcessError as err:
            #process terminated with returncode != 0
            message = _('Process failed (error code: %s). Message: %s')
            message = message  % (str(err.returncode), err.output[-1000:])
            _logger.error(message)
            raise UserError(message) 
        except TimeoutExpired as err:
            #process did not terminate within timeout, and was killed
            #please notice by now (2017-10-17) there is some bug in subprocess32, line 1190, that could affect this
            message = _('Process did not terminate within %s seconds. Message: %s')
            message = message  % (str(err.timeout), err.output[-1000:])
            _logger.error(message)
            raise UserError(message) 
        except:
            #IOError?
            import sys, traceback
            message = _("Exception while running external process: %s") % str(sys.exc_info()[1])
            _logger.error(traceback.format_exc())
            #message = message % format_exc
            #message = message % (str(sys.exc_info()[0]),str(sys.exc_info()[1]))
            #_logger.error(sys.exc_info()[2])
            raise UserError(message)
	   
    @api.noguess
    def report_action(self, docids, data=None, config=True):
        report_act = super(IrActionsReport, self).report_action(docids, data, config)

        if self.direct_print:
            data, dataformat = self.render_qweb_pdf(report_act.get('context')['active_ids'], report_act.get('data'))
            self._direct_report_print(data)
            return
        else:
            return report_act
