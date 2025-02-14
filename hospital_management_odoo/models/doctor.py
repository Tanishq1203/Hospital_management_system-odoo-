# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HospitalDoctor(models.Model):
    """New Class : This class is contain the fields and logical
    methods and functions related to the doctore data"""

    _name = "hospital.doctor"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Hospital Doctor"
    _rec_name = "doctor_name"

    doctor_name = fields.Char(string="Name", required=True, tracking=True)
    tags = fields.Many2many(comodel_name="hospital.tags", string="Specialization")
    age = fields.Integer(string="Age", tracking=True, copy=False)
    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        required=True,
        default="male",
        tracking=True,
    )
    note = fields.Text(string="Description")
    image = fields.Binary(string="Patient Image")
    appointment_count = fields.Integer(
        string="Appointment Count", compute="_compute_appointment_count"
    )
    active = fields.Boolean(string="Active")
    color = fields.Integer(string="Color")
    # -----------------------------------
    # ----------ORM-METHOD---------------
    # -----------------------------------

    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get("doctor_name"):
            default["doctor_name"] = _("%s (Copy)", self.doctor_name)
        default["note"] = "Copied Record"
        return super(HospitalDoctor, self).copy(default)

    def _compute_appointment_count(self):
        """NEW - COMPUTE - METHOD :That mrthod is use to count the
        number of total appointments"""
        for rec in self:
            appointment_count = self.env["hospital.appointment"].search_count(
                [("doctor_id", "=", rec.id)]
            )
            rec.appointment_count = appointment_count
