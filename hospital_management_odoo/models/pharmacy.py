from odoo import models, fields, api


class Medicine(models.Model):
    """New - class : This class contain the fields and method related
    to the pharmacy medicines"""

    _name = "pharmacy.medicine"
    _description = "Medicine"

    name = fields.Char(string="Medicine Name", required=True)
    description = fields.Text(string="Description")
    price = fields.Float(string="Price", required=True)
    stock_quantity = fields.Integer(string="Stock Quantity", required=True)
    units = fields.Selection(
        [
            ("kilogram", "Kg"),
            ("gram", "g"),
            ("milligram", "mg"),
            ("microgram", " mcg/μg"),
            ("litre", "l"),
            ("millilitre", "ml"),
            ("cubic centimetre", "cc"),
            ("mole", "mol"),
            ("millimole", "mmol"),
        ]
    )
