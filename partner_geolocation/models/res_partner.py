# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from random import choice
from string import digits

from odoo import models, fields, api, exceptions, _
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"
    _description = "Partner"

    @api.multi
    def action_open_geolocate_widget(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.client',
            'name': 'Confirm',
            'tag': 'partner_geolocation_geolocate_confirm',
            'target': 'main',
            'partner_id': self.id,
            'partner_name': self.display_name,
            'partner_street': self.street,
            'partner_city': self.city,
            'partner_country_id': self.country_id,
            'partner_mobile': self.mobile
        }
        return action
    
    @api.multi
    def geolocate_manual(self, next_action, location=False):
        self.ensure_one()
        _logger.warning("geolocate_manual")
        return self.geolocate_action(next_action, location)

    @api.multi
    def geolocate_action(self, next_action, location):
        """ Changes the geolocation of the partner.
            Returns an action to the geolocate message,
            next_action defines which menu the geolocate message should return to. ("My Geolocation" or "Geolocate Mode")
        """
        self.ensure_one()
        action_message = self.env.ref('partner_geolocation.partner_geolocation_action_location_message').read()[0]
        action_message['previous_geolocate_change_date'] = self.date_localization or False
        action_message['partner_name'] = self.name
        action_message['next_action'] = next_action

        modified_partner = self.sudo(self._uid).geolocate_action_change(location)
        action_message['partner'] = modified_partner.read()[0]
        _logger.warning("geolocate_manual action")
        _logger.warn(action_message)
        return {'action': action_message}

    @api.multi
    def geolocate_action_change(self, location):
        """ Geolocate action
            Geolocate: modify latituge and longitude field of the partner record
        """
        if len(self) > 1:
            raise exceptions.UserError(_('Cannot perform geolocate action on multiple employees.'))
        # action_date = fields.Datetime.now()

        if location:
            self.write({
                    'partner_latitude': location[0],
                    'partner_longitude': location[1],
                    'date_localization': fields.Date.context_today(self)
                })
        else:
            raise exceptions.UserError(_('Cannot perform geolocate action on %(part_name)s, could not find a valid geo-location. '
                'Your device might have blocked location, please give access to location.') % {'part_name': self.name, })
        return self