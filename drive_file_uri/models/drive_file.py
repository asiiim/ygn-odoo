# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

import requests

from odoo import api, fields, models, _
from odoo.osv import expression


class DriveFile(models.Model):
    _name = "drive.file"
    _description = 'Google Drive File'
    _rec_name = 'res_url'
    _order = "sequence, name, res_url, id"
    
    sequence = fields.Integer(string="Sequence")
    name = fields.Char(string="Resource Name", compute='_get_resource_details', store=True, help="Resource name is generated from the link.")
    res_url = fields.Text(string="Drive URI", required=True, help="Input/Paste the link from Get Shareable Link menu with anyone with link can view access turned on.")
    res_id = fields.Char(string='Resource Id', compute='_get_resource_details', store=True)

    _sql_constraints = [
        ('res_id_key', 'unique (res_id)', 'This resource id already exists, please enter other resource id!')
    ]

    @api.depends('res_url')
    def _get_resource_details(self):
        for r in self:
            if not r.res_url:
                pass
            else:
                # Extract id
                temp_res = ["0"]
                if "https://drive.google.com/file/d/" in r.res_url:
                    # eg https://drive.google.com/file/d/1PyCCNaXKtFdRSm0M1eEFaiSfrU_REwhW/view?usp=sharing
                    temp_res1 = r.res_url.split("https://drive.google.com/file/d/",1)
                    if len(temp_res1) > 1 and temp_res1[0] == "" and "/view?usp=sharing" in temp_res1[1]:
                        temp_res = temp_res[1].split("/view?usp=sharing",1)
                        # reverse the items for consistency
                        temp_res.reverse()
                elif "https://drive.google.com/open?id=" in r.res_url:
                    # eg https://drive.google.com/open?id=1prW58T6Y8YmQn6cw4WIcSv1daGKX0lI9
                    temp_res = r.res_url.split("https://drive.google.com/open?id=",1)
                if len(temp_res) > 1 and temp_res[0] == '':
                    r.res_id = temp_res[1]
                    # Now Extract filename
                    url = "https://drive.google.com/uc?export=view&id=%s" % temp_res[1]
                    res = requests.get(url, allow_redirects=True)
                    if res.status_code == 200:
                        r.name = res.headers.get('Content-Disposition').split('filename="')[1].split('";filename*=')[0]

    @api.model
    def default_get(self, default_fields):
        default_name = self._context.get('default_name')
        contextual_self = self.with_context(default_name=default_name)
        return super(DriveFile, contextual_self).default_get(default_fields)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            args = ['|', '|', ('res_url', operator, name), ('res_id', operator, name), ('name', operator, name)] + args
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        # self.search(domain + args, limit=limit)
        # return partners.name_get()
        return super(DriveFile, self).name_search(name, args, operator=operator, limit=limit)

    @api.multi
    def action_zoom_image(self):
        """
        Zooms the current google drive file.
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'drive.file',
            'name': self.name,
            'res_id': self.id,
            # 'view_mode': 'form',
            # 'view_id': product_tmpl_zoom_view_id,
            'views': [(self.env.ref('drive_file_uri.drive_file_zoom_view').id, 'kanban')],
            'domain': [('id','=',self.id)],
            'target': 'new',
            'context': dict(
                self.env.context,
            ),
        }
    
    # @api.multi
    # @api.depends('name', 'code')
    # def name_get(self):
    #     result = []
    #     for note in self:
    #         if not note.code:
    #             name = note.name
    #         else:
    #             name =  '[' + note.code + '] ' + note.name
    #         result.append((note.id, name))
    #     return result
