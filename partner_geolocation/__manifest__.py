# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    'name': 'Partner Geolocation - GPS',
    'summary': """
        With this module the location of a partner can be geolocated using smart phone's gps.""",
    'version': '11.0.1.0.0',
    'license': 'OPL-1',
    'author': 'Bishal Pun,'
              'Ygen Software Pvt. Ltd.',
    'website': 'https://ygen.io',
    'price': 50.00,
    'currency': 'EUR',
    'depends': [
        'decimal_precision',
        'base_geolocalize',
    ],
    'data': [
        'views/web_asset_backend_template.xml',
        'views/res_partner_view.xml',
        'data/location_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'qweb': [
        "static/src/xml/geolocation.xml",
    ],
    'application': True,
}