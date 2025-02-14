# Import Statement
from random import randint
from odoo import fields, models


class Tag(models.Model):
    # New Method : Manage and store tags .
    _name = "hospital.tags"
    _description = "Tags"

    def _get_default_color(self):
        return randint(1, 11)

    # Fields
    name = fields.Char(string="Tag Name", required=True, translate=True)
    color = fields.Integer(string="Color", default=_get_default_color)

    # SQL Constraint : check the tag name is unique
    # Syntax [name , sql_defination , message]
    _sql_constraints = [
        ("name_uniq", "unique (name)", "Tag name already exists!"),
    ]
