from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    related_chamber = fields.Char(related='partner_id.chamber', store=True)
