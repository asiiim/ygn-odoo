from odoo import api, fields, models


class ResCompany(models.Model):
    """Add chamber number field in company model"""
    _inherit = "res.company"

    chamber = fields.Char('Chamber No.')

    _sql_constraints = [
        ('unique_chamber', 'unique (chamber)', 'This chamber no. is already registered in the system !'),
    ]
