from odoo import models, fields


class PatientInvoice(models.Model):
    """Inherited -class : For add custom fields and logic and overrride the methods"""

    _inherit = "account.move"
    _description = "Inherited account move for invoice facility."

    patient_id = fields.Many2one(comodel_name="hospital.patient", string="Patient Name")
    doctor_id = fields.Many2one(comodel_name="hospital.doctor", string="Doctor Name")
    appointment_id = fields.Many2one(
        comodel_name="hospital.appointment", string="Appointment ID"
    )
    medicine_ids = fields.Many2many(
        comodel_name="pharmacy.medicine", string="Medicines"
    )
