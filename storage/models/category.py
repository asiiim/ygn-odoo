# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StorageCategory(models.Model):
    _name = 'storage.category'
    _order = "sequence, name"

    name = fields.Char("Name")
    
    sequence = fields.Integer(help="Gives the sequence order when displaying a list of categories.")

    diptest_id = fields.Many2one('storage.diptest', string="Dip Test Formula")
    
    formula = fields.Text(string="Volume Storage Formula",
        help="Formula to calculate the volume of the storage.\n\n"
             "You can include the possible parameter with logical expressions in the field "
             "(for example, use '%(length)f' to display the field 'length') plus"
             "\n%(breadth)f: the breadth of the storage"
             "\n%(height)f: the height of the storage"
             "\n%(diameter)f: the diameter of the storage"
             "\n%(PI)f: value of the Pi",
        default='%(length)f*%(breadth)f*%(height)f*%(diameter)f')

    diptest_formula = fields.Text(string="Dip Test Formula",
        help="Formula to calculate the filled volume of product in the storage by Dip Test.\n\n"
             "You can include the possible parameter with logical expressions in the field "
             "(for example, use '%(length)f' to display the field 'length') plus"
             "\n%(breadth)f: the breadth of the storage"
             "\n%(height)f: the height of the storage"
             "\n%(diameter)f: the diameter of the storage"
             "\n%(PI)f: value of the Pi",
        default='%(length)f*%(breadth)f*%(height)f*%(diameter)f')


