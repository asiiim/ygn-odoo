# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

import time
import io
import logging
import tempfile
from datetime import datetime

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

from odoo.addons.odoo_backup_sh.models.odoo_backup_sh import (
    ModuleNotConfigured,
    compute_backup_filename,
    compute_backup_info_filename,
    get_backup_by_id,
)

try:
    from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
    from apiclient import errors
except ImportError as err:
    logging.getLogger(__name__).debug(err)


_logger = logging.getLogger(__name__)


class BackupConfigTeamDrive(models.Model):
    _inherit = "odoo_backup_sh.config"

    @api.model
    def make_backup_google_drive(
        self, ts, name, dump_stream, info_file, info_file_content, cloud_params
    ):
        # Upload two backup objects to Google Drive
        GoogleDriveService = self.env["ir.config_parameter"].get_google_drive_service()
        folder_id = self.env["ir.config_parameter"].get_param(
            "odoo_backup_sh_google_disk.google_disk_folder_id"
        )
        db_metadata = {
            "name": compute_backup_filename(
                name, ts, info_file_content.get("encrypted")
            ),
            "parents": [folder_id],
        }
        info_metadata = {
            "name": compute_backup_info_filename(name, ts),
            "parents": [folder_id],
        }
        db_mimetype = "application/zip"
        info_mimetype = "text/plain"
        dump_stream.seek(0)
        info_file.seek(0)
        for obj, mimetype, metadata in [
            [dump_stream, db_mimetype, db_metadata],
            [info_file, info_mimetype, info_metadata],
        ]:
            media = MediaIoBaseUpload(obj, mimetype, resumable=True)
            GoogleDriveService.files().create(
                body=metadata, supportsAllDrives=True, media_body=media, fields="id,owners"
            ).execute()
        