# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
import datetime
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class CustomLabRequest(models.Model):
    _inherit = 'lab.request'
    
    text_after_result = fields.Html('Text After Result')
    text_before_result = fields.Html('Text Before Result')
    text_before_result = fields.Html('Text Before Result')
    specimen = fields.Selection(string='Specimen',selection=[('semen','Semen'),('fss','Fresh Sterile Stool'),('fsu','Fresh Sterile Urine'),('bd','Blood'),('sp','SERUM/PLASMA'),('serum','SERUM'),('edta','EDTA BLOOD'),('fss','FRESH STERILE SAMPLE'),('fu','FRESH URINE'),('fs','FRESH STOOL'),('wb','WHOLE BODY')])
    patient_type = fields.Selection(string='Patient Type',selection=[('in','Indoor'),('out','Outdoor')])
    sample_id = fields.Char(string='Sample ID') 
    lab_request_specimen_ids = fields.Many2many('lab.specimen', 'lab_request_specimen_rel', 'request_id', 'speciment_id', string='Specimen',)
    signature_id = fields.Many2one(string='Signature', comodel_name='signature.name', ondelete='set null')
    
class CustomSignatureTemplate(models.Model):
    _inherit = 'signature.name'
    
    request_ids = fields.One2many(string='Lab Request', comodel_name='lab.request', inverse_name='signature_id')

class LabSpecimen(models.Model):
    _name = 'lab.specimen'

    name = fields.Char(string=u'Name',)
    specimen_ids = fields.Many2many('lab.request', 'lab_request_specimen_rel', 'speciment_id', 'request_id', string='Lab Request')

class CustomLabTest(models.Model):
    _inherit = 'lab.test'
    
    text_after_result = fields.Html('Text After Result')
    text_before_result = fields.Html('Text Before Result')
    text_before_result = fields.Html('Text Before Result')

class CustomLabTestAttribute(models.Model):
    _inherit = 'lab.test.attribute'

    method = fields.Char(string="Method")
    status = fields.Char(string="Status")

class CustomLabPatient(models.Model):
    _inherit = 'lab.patient'
    
    phone = fields.Char(string="Phone", required=False)
    email = fields.Char(string="Email", required=False)
    dob = fields.Date(string='Date Of Birth', required=False)
    mobile = fields.Char(string="Mobile", copy=False)

    @api.multi
    def compute_age(self):
        for data in self:
            if data.dob:
                dob = fields.Datetime.from_string(data.dob)
                date = fields.Datetime.from_string(data.date)
                delta = relativedelta(date, dob)
                data.age = str(delta.years) + ' years & ' + str(delta.months) + ' months'
    @api.onchange('patient')
    def detail_get_mobile(self):
        self.mobile = self.patient.mobile

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
                                                'request_line': [(0, 0, {'test_content':x.test_content.id,
                                                                        'unit': x.unit.id,
                                                                        'method': x.method,
                                                                        'interval': x.interval}) for x in line.lab_test.test_lines],
                                                })
            self.state = 'request_lab'
        else:
            raise UserError(_('Please Select Lab Test.'))