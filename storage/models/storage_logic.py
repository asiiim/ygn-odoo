# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StorageLogic(models.Model):
    _name = 'storage.logic'

    name = fields.Char("Name")

    formula = fields.Text(string="Volume Storage Formula",
        help="Formula to calculate the volume of the storage.\n\n"
             "You can include the possible parameter with logical expressions in the field "
             "(for example, use '%(length)f' to display the field 'length') plus"
             "\n%(breadth)f: the breadth of the storage"
             "\n%(height)f: the height of the storage"
             "\n%(radius)f: the radius of the storage"
             "\n%(PI)f: value of the Pi",
        default='%(length)f*%(breadth)f*%(height)f*%(radius)f')

    storage_type = fields.Char("Storage Type", 
    	help="Provide the name of the storage type. \n\n"
    			"For Example: \n\n"
    			"1. Horizontal Cylinder Tank, \n"
    			"2. Vertical Cylinder Tank, \n"
    			"3. Rectangle Tank, \n"
    			"4. Horizontal Oval Tank, \n"
    			"5. Vertical Oval Tank, \n"
    			"6. Horizontal Capsule Tank, \n"
    			"7. Vertical Capsule Tank etc. \n")
