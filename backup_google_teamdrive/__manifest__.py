# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    "name": """Google drive backing up - Team Drive | Shared Drive""",
    "summary": """Use your Team or Shared Drive's storage. Allows you to use your Team Drive's storage instead of service account's.""",
    "category": "Backup",
    # "live_test_url": "",
    "images": ["images/google drive backing up.jpg"],
    "version": "11.0.1.0.0",
    "application": False,
    "author": "Ygen Software Pvt. Ltd., Bishal Pun",
    "support": "apps@ygen.io",
    "website": "https://ygen.io/",
    "license": "OPL-1",  # MIT
    "price": 60.00,
    "currency": "EUR",
    "depends": ["odoo_backup_sh_google_disk"],
    "external_dependencies": {"python": ["googleapiclient"], "bin": []},
    "data": [
    ],
    "qweb": [],
    "demo": [],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,
    "auto_install": False,
    "installable": True,
}
