# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
import datetime
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CustomLabRequest(models.Model):
    _inherit = 'lab.request'
    
    text_after_result = fields.Html('Text After Result')
    text_before_result = fields.Html('Text Before Result')

class CustomLabTest(models.Model):
    _inherit = 'lab.test'
    
    text_after_result = fields.Html('Text After Result')
    text_before_result = fields.Html('Text Before Result')

class CustomLabAppointment(models.Model):
    _inherit = 'lab.appointment'
    
    @api.multi
    def action_request(self):
        if self.appointment_lines:
            for line in self.appointment_lines:
                data = self.env['lab.test'].search([('lab_test', '=', line.lab_test.lab_test)])
                self.env['lab.request'].create({'lab_request_id': self.name,
                                                'app_id': self.id,
                                                'lab_requestor': self.patient_id.id,
                                                'lab_requesting_date': self.appointment_date,
                                                'test_request': line.lab_test.id,
                                                'text_after_result': line.lab_test.text_after_result,
                                                'text_before_result': line.lab_test.text_before_result,
                                                'request_line': [(6, 0, [x.id for x in data.test_lines])],
                                                })
            self.state = 'request_lab'
        else:
            raise UserError(_('Please Select Lab Test.'))