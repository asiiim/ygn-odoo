from odoo import api, fields, models, tools, _

import logging
_logger = logging.getLogger(__name__)


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    bank_account_id = fields.Many2one('res.partner.bank', 'Payroll Bank Account', help='The bank account from where the payroll is provided to the employee.')