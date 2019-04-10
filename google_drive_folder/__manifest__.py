# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    'name': 'Google Drive™ Folder integration',
    'version': '0.1',
    'category': 'Extra Tools',
    'installable': True,
    'auto_install': False,
    'data': [
        'views/google_drive_views.xml',
        'views/google_drive_templates.xml',
    ],
    'demo': [
        'data/google_drive_demo.xml'
    ],
    'depends': ['base_setup', 'google_drive'],
    'description': """
Integrate google folder to Odoo record.
============================================

This module allows you to integrate google folders to any of your Odoo record quickly and easily using OAuth 2.0 for Installed Applications,
You can configure your google Authorization Code from Settings > Configuration > General Settings by clicking on "Generate Google Authorization Code"
"""
}
