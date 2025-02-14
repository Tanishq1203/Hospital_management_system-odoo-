from odoo import models, fields


class SaleOrderLine(models.Model):
    # Inherited Class

    _inherit = "sale.order.line"

    medicine_ids = fields.Many2many(
        comodel_name="pharmacy.medicine", string="Medicines"
    )
