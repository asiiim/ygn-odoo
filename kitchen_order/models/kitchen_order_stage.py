# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

AVAILABLE_PRIORITIES = [
    ('0', 'Normal'),
    ('1', 'Low'),
    ('2', 'High'),
    ('3', 'Very High'),
]

class Stage(models.Model):
    """ Model for case stages. This models the main stages of a kitchen order flow. 
    """
    _name = "kitchen_order.stage"
    _description = "Stage of Kitchen Order"
    _rec_name = 'name'
    _order = "sequence, name, id"


    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    requirements = fields.Text('Requirements', help="Enter here the internal requirements for this stage (ex: Offer sent to customer). It will appear as a tooltip over the stage's name.")
    legend_priority = fields.Text('Priority Management Explanation', translate=True,
        help='Explanation text to help users using the star and priority mechanism on stages or issues that are in this stage.')
    fold = fields.Boolean('Folded in Kitchen Orders',
        help='This stage is folded in the kanban view when there are no records in that stage to display.')
