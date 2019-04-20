# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    # Create function for returning all data required
    # for seal line ids
    def report_get_seal_lines(self):
        chamber_list = self._report_chamber_list()
        upseal_res = ['-']*len(chamber_list)
        downseal_res = ['-']*len(chamber_list)

        for seal_line in sorted(self.seal_line_ids.filtered(lambda r: r.seal_type.name == "Up Seal"), key=lambda x: x.chamber_id.name):

            if seal_line.chamber_id.name in chamber_list:
                upseal_res[chamber_list.index(seal_line.chamber_id.name)] = seal_line.name

        for seal_line in sorted(self.seal_line_ids.filtered(lambda r: r.seal_type.name == "Down Seal"), key=lambda x: x.chamber_id.name):
            if seal_line.chamber_id.name in chamber_list:
                downseal_res[chamber_list.index(seal_line.chamber_id.name)] = seal_line.name
        
        master_res = self.seal_line_ids.filtered(lambda r: r.seal_type.name == "Master Seal")
        if master_res:
            master_seal = master_res[0].name
        else: 
            master_seal = "-"

        return {
            'chamber_list': chamber_list,
            'upseal_list': upseal_res,
            'downseal_list': downseal_res,
            'masterseal': master_seal
        }

    def _report_chamber_list(self):
        res = []
        for seal_line in self.seal_line_ids.filtered(lambda r: r.chamber_id):
            res.append(seal_line.chamber_id.name)
        return sorted(list(dict.fromkeys(res)))
