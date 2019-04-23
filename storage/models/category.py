# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class StorageCategory(models.Model):
    _name = 'storage.category'
    _order = "sequence, name"

    name = fields.Char("Name")
    
    sequence = fields.Integer(help="Gives the sequence order when displaying a list of categories.")
    
    formula = fields.Text(string="Volume Storage Formula",
        help="Formula to calculate the volume of the storage.\n\n"
             "You can include the possible parameter with logical expressions in the field "
             "(for example, use '%(length)f' to display the field 'length') plus"
             "\n%(breadth)f: the breadth of the storage"
             "\n%(height)f: the height of the storage"
             "\n%(diameter)f: the diameter of the storage"
             "\n%(pi)f: value of the Pi",
        default='%(length)f*%(breadth)f*%(height)f*%(diameter)f')

    diptest_formula = fields.Text(string="Dip Test Formula",
        help="Formula to calculate the filled volume of product in the storage by Dip Test.\n\n"
             "You can include the possible parameter with logical expressions in the field "
             "(for example, use '%(length)f' to display the field 'length') plus"
             "\n%(breadth)f: the breadth of the storage"
             "\n%(height)f: the height of the storage"
             "\n%(diameter)f: the diameter of the storage"
             "\n%(dip)f: the dip value"
             "\n%(pi)f: value of the Pi",
        default='%(length)f*%(breadth)f*%(height)f*%(dip)f')


