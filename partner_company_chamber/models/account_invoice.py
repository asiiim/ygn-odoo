from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    related_coc = fields.Char(related='partner_id.coc_registration_number', store=True)
