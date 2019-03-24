from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    related_chamber = fields.Char(related='partner_id.chamber')
