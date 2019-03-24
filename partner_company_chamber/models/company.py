from odoo import api, fields, models


class ResPartner(models.Model):
    """Add chamber number field in company model"""
    _inherit = "res.company"

    chamber = fields.Char('Chamber Number')
