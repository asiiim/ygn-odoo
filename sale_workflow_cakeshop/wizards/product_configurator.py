# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductConfiguratorSale(models.TransientModel):

    _name = 'product.configurator.ordernow'
    _inherit = 'product.configurator'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        required=True,
        readonly=False,
        string="Partner"
    )
    requested_date = fields.Datetime(string='Requested Date', required=True, index=True, copy=False, default=fields.Datetime.now)
    client_order_ref = fields.Char(string='Customer Reference', copy=False)
    amount = fields.Monetary(string='Advance Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)

    def _get_order_line_vals(self, product_id):
        """Hook to allow custom line values to be put on the newly
        created or edited lines."""
        product = self.env['product.product'].browse(product_id)

        return {
            'product_id': product_id,
            'name': product._get_mako_tmpl_name(),
            'product_uom': product.uom_id.id,
        }

    @api.multi
    def action_config_done(self):
        """Parse values and execute final code before closing the wizard"""
        res = super(ProductConfiguratorSale, self).action_config_done()

        # Call order configurator wizard
        line_vals = self._get_order_line_vals(res['res_id'])
        
        if self.order_line_id:
            self.order_line_id.write(line_vals)
        else:
            self.order_id.write({'order_line': [(0, 0, line_vals)]})

        return
