# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.
import logging
import json
import re

import requests
import werkzeug.urls

from odoo import api, fields, models
from odoo.exceptions import RedirectWarning, UserError
from odoo.tools.translate import _

from odoo.addons.google_account.models.google_service import GOOGLE_TOKEN_ENDPOINT, TIMEOUT

_logger = logging.getLogger(__name__)


class GoogleDrive(models.Model):

    _inherit = 'google.drive.config'

    @api.multi
    def get_google_drive_folder_url(self, res_id, template_id):
        self.ensure_one()
        self = self.sudo()

        # overriding get_google_drive_url is also an option
        # but browse query takes extra resources.
        # So instead create new method to resolve this one.

        model = self.model_id
        filter_name = self.filter_id.name if self.filter_id else False
        record = self.env[model.model].browse(res_id).read()[0]
        record.update({
            'model': model.name,
            'filter': filter_name
        })
        name_gfolds = self.name_template
        try:
            name_gfolds = name_gfolds % record
        except:
            raise UserError(_("At least one key cannot be found in your Google Drive name pattern"))

        attachments = self.env["ir.attachment"].search([('res_model', '=', model.model), ('name', '=', name_gfolds), ('res_id', '=', res_id)])
        url = False
        if attachments:
            url = attachments[0].url
        else:
            url = self.copy_folder(res_id, template_id, name_gfolds, model.model).get('url')
        _logger.warning("******** url is : " + url)
        return url

    @api.model
    def copy_folder(self, res_id, template_id, name_gfolds, res_model):
        google_web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        access_token = self.get_access_token()

        # Copy template in to drive with help of new access token
        request_url = "https://www.googleapis.com/drive/v2/files/%s?access_token=%s" % (template_id, access_token)
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        try:
            req = requests.get(request_url, headers=headers, timeout=TIMEOUT)
            req.raise_for_status()
            template = req.json()
        except requests.HTTPError:
            raise UserError(_("The Google Template cannot be found. Maybe it has been deleted."))

        record_url = "Click on link to open Record in Odoo\n %s/?db=%s#id=%s&model=%s" % (google_web_base_url, self._cr.dbname, res_id, res_model)
        configs = {
            "google_web_base_url": google_web_base_url,
            "access_token": access_token,
            "record_url": record_url
        }
        parents = []
        for parent in template["parents"]:
            parents.append({"id": parent.get("id")})
        folder = self._copy_file_folder_rec(template, parents, configs, name_gfolds)
        res = {}
        if folder.get('alternateLink'):
            res['id'] = self.env["ir.attachment"].create({
                'res_model': res_model,
                'name': name_gfolds,
                'res_id': res_id,
                'type': 'url',
                'url': folder['alternateLink']
            }).id
            # Commit in order to attach the document to the current object instance, even if the permissions has not been written.
            self._cr.commit()
            res['url'] = folder['alternateLink']
            
            # Give permissions
            self._write_permissions(res, configs)
            
        return res
    
    def _write_permissions(self, res, configs):
        key = self._get_key_from_url(res['url'])
        _logger.warning("key-> " + key)
        request_url = "https://www.googleapis.com/drive/v2/files/%s/permissions?emailMessage=This+is+a+drive+folder+created+by+Odoo&sendNotificationEmails=false&access_token=%s" % (key, configs["access_token"])
        headers = {
            'Content-type': 'application/json',
            'Accept': 'text/plain'
        }

        # Check for custom permission and write those to resources
        if self.g_permission:
            data = {'role': self.g_role, 'type': self.g_type, 'value': self.g_value, 'withLink': self.g_withLink}
            try:
                req = requests.post(request_url, data=json.dumps(data), headers=headers, timeout=TIMEOUT)
                req.raise_for_status()
            except requests.HTTPError:
                raise self.env['res.config.settings'].get_config_warning(_("The permission '%s' for 'anyone with the link' has not been written on the document" % (self.g_type)))
        
        # Default permission
        if self.g_user_permission and self.env.user.email:
            data = {'role': 'writer', 'type': 'user', 'value': self.env.user.email}
            try:
                requests.post(request_url, data=json.dumps(data), headers=headers, timeout=TIMEOUT)
            except requests.HTTPError:
                pass

    def _copy_file_folder_rec(self, template, parents, configs, name_gfolds=None):
        # Check if it is a folder
        if template.get("mimeType") == "application/vnd.google-apps.folder":
            # Do folder work here
            # Create folder and attach to parent
            folder = self._create_folder(name_gfolds, parents, configs)
            parents = [
                {
                    "id": folder["id"]
                }
            ]
            children = self._has_children(template.get("id"), configs)
            if children["children"]:
                for child_fold in children["content"].get("items"):
                    self._copy_file_folder_rec(child_fold, parents, configs, name_gfolds=child_fold.get("title"))
            
            return folder
        self._copy_file(name_gfolds, template["id"], parents, configs)
        # Else
        # Do file work here

        return

    def _has_children(self, res_id, configs):
        # request_url = "https://www.googleapis.com/drive/v2/files/%s/children?access_token=%s" % (res_id, configs["access_token"])
        request_url = "https://www.googleapis.com/drive/v2/files?q='%s'+in+parents&access_token=%s" % (res_id, configs["access_token"])
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        try:
            req = requests.get(request_url, headers=headers, timeout=TIMEOUT)
            req.raise_for_status()
            content = req.json()
            if content["items"]:
                return {'children': True, 'content': content}
            return {'children': False, 'content': content}
        except requests.HTTPError:
            raise UserError(_("The Google Template cannot be found. Maybe it has been deleted."))

    def _is_folder(self, res_id, configs):
        request_url = "https://www.googleapis.com/drive/v2/files/%s?fields=id,mimeType,title&access_token=%s" % (res_id, configs["access_token"])
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        try:
            req = requests.get(request_url, headers=headers, timeout=TIMEOUT)
            req.raise_for_status()
            content = req.json()
            if content.get("mimeType") and content["mimeType"] == "application/vnd.google-apps.folder":
                return {'folder': True, 'content': content}
            return {'folder': False, 'content': content}
        except requests.HTTPError:
            raise UserError(_("The Google Template cannot be found. Maybe it has been deleted."))

    def _create_folder(self, folder_name, dest_parents, configs):
        data = {
            "title": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "description": configs["record_url"],
            "parents": dest_parents
        }

        request_url = "https://www.googleapis.com/drive/v2/files?access_token=%s" % (configs["access_token"])
        headers = {
            'Content-type': 'application/json'
        }
        req = requests.post(request_url, data=json.dumps(data), headers=headers, timeout=TIMEOUT)
        req.raise_for_status()
        return req.json()

    def _copy_file(self, file_name, template_id, dest_parents, configs):
        data = {
            "title": file_name,
            "description": configs["record_url"],
            "parents": dest_parents
        }
        request_url = "https://www.googleapis.com/drive/v2/files/%s/copy?access_token=%s" % (template_id, configs["access_token"])
        headers = {
            'Content-type': 'application/json',
            'Accept': 'text/plain'
        }
        req = requests.post(request_url, data=json.dumps(data), headers=headers, timeout=TIMEOUT)
        req.raise_for_status()
        return req.json()
    
    folder = fields.Boolean('Is a Folder', default=False)
    g_role = fields.Selection([
        ('owner', 'Owner'),
        ('organizer', 'Organizer'),
        ('fileOrganizer', 'File Organizer'),
        ('writer', 'Writer'),
        ('reader', 'Reader')], string='Drive Permission Role', default='writer',
        help='An owner is highest level of role. Use this role carefully.\n'
            'Organizer and File Organizer are as the name says.\n'
            'A writer can edit the files and folders.\n'
            'A reader can view files and folders.')
    g_type = fields.Selection([
        ('user', 'User'),
        ('group', 'Group'),
        ('domain', 'Domain'),
        ('anyone', 'Anyone')], string='Drive Permission Type', default='anyone',
        help='The account type.\n'
            'A user, group, domain needs value.\n'
            'Anyone type is public.')
    g_value = fields.Text(
        'Value', translate=True,
        help="The email address or domain name for the entity. This is used during inserts "
            "and is not populated in responses. When making a drive.permissions.insert request," 
            "exactly one of the id or value fields must be specified unless the permission type "
            "is anyone, in which case both id and value are ignored. ")
    g_withLink = fields.Boolean('Anyone with the link', default=False, 
        help="Whether the link is required for this permission.")
    g_permission = fields.Boolean('Custom Permission', default=False, 
    help="Create your own custom permission.")
    g_user_permission = fields.Boolean('Share to user', default=False,
        help="Whether to add current user to the resource.")
    def _get_key_from_url(self, url):
        word = super(GoogleDrive, self)._get_key_from_url(url)
        if word:
            return word
        word = re.search("(key=|/folders/)([A-Za-z0-9-_]+)", url)
        if word:
            return word.group(2)
        return None
