from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    related_coc = fields.Char(related='partner_id.coc_registration_number', store=True)
