from odoo import models, fields


class PatientHistory(models.Model):
    _name = "hospital.patient.history"
    _description = "Patient History"

    patient_id = fields.Many2one("hospital.patient", string="Patient", required=True)
    appointment_id = fields.Many2one(
        "hospital.appointment", string="Appointment", required=True
    )
    notes = fields.Text(string="Notes")
    date = fields.Datetime(string="Date", default=fields.Datetime.now)
