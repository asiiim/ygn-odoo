from odoo import api, fields, models


class ResCompany(models.Model):
    """Add chamber number field in company model"""
    _inherit = "res.partner"

    _sql_constraints = [
        ('unique_coc', 'unique (coc_registration_number)', 'This chamber no. is already registered in the system !'),
    ]
