from odoo import api, fields, models


class ResCompany(models.Model):
    """Add chamber number field in company model"""
    _inherit = "res.partner"

    chamber = fields.Char('Chamber Number')

    _sql_constraints = [
        ('unique_chamber', 'unique (chamber)', 'This chamber no. is already registered in the system !'),
    ]
