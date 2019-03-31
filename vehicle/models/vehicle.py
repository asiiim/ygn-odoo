# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Vehicle(models.Model):
    _name="vehicle.vehicle"
    _description = 'Vehicle'
    _order = 'sequence, name'

    name=fields.Char(string="Name")
    sequence = fields.Integer(help='Used to order Vehicles', default=10)

