# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.addons import decimal_precision as dp

class HrContract(models.Model):
    _inherit = 'hr.contract'

    qualif = fields.Char(string='Qualification')
    niveau = fields.Char()
    coef = fields.Char(string='Coefficient')


class HrPayslip(models.Model):
    _inherit = 'hr.contract'

    allowance_khaja = fields.Float(string="Allowance for khaja", copy=True, help="Allowance for Khaja")
    allowance_khaja_tax = fields.Float(string="Taxable Khaja", copy=True, help="Taxable Khaja")
    allowance_trans = fields.Float(string="Allowance for Transportation", copy=True, help="Allowance for Transportation")
    allowance_trans_tax = fields.Float(string="Taxable Transporation", copy=True, help="Taxable Transporation")
    bonus = fields.Float(string="Bonus", copy=True, help="Bonus")
    emp_grade_amount = fields.Float(string="Employee Grade Amount", copy=True, help="Employee Grade Amount", index=True)
    overtime_buffer_hours = fields.Float(string="Overtime Buffer Hours", copy=True, help="Eg:\nbuffer time is 5 hours then overtime pay will not be calculated if overtime is less or equal to 5 hours.", index=True)
    overtime_pay_factor = fields.Float(string="Overtime Pay Factor", copy=True, help="For example: overtime is 5 hours, overtime_pay_factor is 1.5 and basic salary is 500 per hour then overtime pay = 5 * 500 * 1.5", index=True)
    total_allocated_hours = fields.Float(string="Total Working Hours", copy=True, help="Total working hours")
    undertime_buffer_hours = fields.Float(string="Under-time Buffer Hours", copy=True, help="Under-time Buffer Hours", index=True)
    undertime_fine_factor = fields.Float(string="Under-time Fine Factor", copy=True, help="For Eg:\nundertime_fine_factor is 0.3, salary is 500 per hour and leave hours totals to 5 hours then fine will be as follows:\nfine = 0.2 * 500 * 5", index=True)

    
