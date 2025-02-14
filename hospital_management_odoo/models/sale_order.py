from odoo import models, fields, api


class SaleOrder(models.Model):
    # Inherited class
    _inherit = "sale.order"

    medicine_ids = fields.Many2many(
        comodel_name="pharmacy.medicine", string="Medicines"
    )
