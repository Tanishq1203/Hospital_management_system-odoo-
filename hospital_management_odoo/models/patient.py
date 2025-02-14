# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HospitalPatient(models.Model):
    """New-class : That contains fields and methods and logical functions
    related to the patient data records"""

    _name = "hospital.patient"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Hospital Patient"
    _order = "id desc"

    name = fields.Char(string="Name", required=True, tracking=True)
    reference = fields.Char(
        string="Order Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _("New"),
    )
    age = fields.Integer(string="Age", tracking=True)
    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        required=True,
        default="female",
        tracking=True,
    )
    note = fields.Text(string="Description")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "Confirmed"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        string="Status",
        tracking=True,
    )
    responsible_id = fields.Many2one(comodel_name="res.partner", string="Responsible")
    appointment_count = fields.Integer(
        string="Appointment Count", compute="_compute_appointment_count"
    )
    image = fields.Binary(string="Patient Image")
    appointment_ids = fields.One2many(
        comodel_name="hospital.appointment",
        inverse_name="patient_id",
        string="Appointments",
    )
    invoice_count = fields.Integer(
        string="Invoice Count", compute="_compute_invoice_count"
    )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner")

    @api.model
    def default_get(self, fields):
        res = super(HospitalPatient, self).default_get(fields)
        res["note"] = "NEW Patient Created"
        return res

    def _compute_appointment_count(self):
        for rec in self:
            appointment_count = self.env["hospital.appointment"].search_count(
                [("patient_id", "=", rec.id)]
            )
            rec.appointment_count = appointment_count

    # ------------------------------------------
    # --------------BUTTONS-ACTIONS-------------
    # ------------------------------------------
    def action_confirm(self):
        for rec in self:
            rec.state = "confirm"

    def action_done(self):
        for rec in self:
            rec.state = "done"

    def action_draft(self):
        for rec in self:
            rec.state = "draft"

    def action_cancel(self):
        for rec in self:
            rec.state = "cancel"

    # -------------------------------------
    # ------------ORM-METHODS--------------
    # -------------------------------------

    @api.model
    def create(self, vals):
        if not vals.get("note"):
            vals["note"] = "New Patient"
        if vals.get("reference", _("New")) == _("New"):
            vals["reference"] = self.env["ir.sequence"].next_by_code(
                "hospital.patient"
            ) or _("New")
        res = super(HospitalPatient, self).create(vals)
        return res

    @api.constrains("name")  # Decorator
    def check_name(self):
        for rec in self:
            patients = self.env["hospital.patient"].search(
                [("name", "=", rec.name), ("id", "!=", rec.id)]
            )
            if patients:
                raise ValidationError(_("Name %s Already Exists" % rec.name))

    @api.constrains("age")
    def check_age(self):
        for rec in self:
            if rec.age == 0:
                raise ValidationError(_("Age Cannot Be Zero .. !"))

    def name_get(self):
        result = []
        for rec in self:
            name = "[" + rec.reference + "] " + rec.name
            result.append((rec.id, name))
        return result

    # ------------------------------------------
    # --------------BUTTONS-ACTIONS-------------
    # ------------------------------------------

    def action_open_appointments(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Appointments",
            "res_model": "hospital.appointment",
            "domain": [("patient_id", "=", self.id)],
            "context": {"default_patient_id": self.id},
            "view_mode": "tree,form",
            "target": "current",
        }

    def action_open_invoices(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Invoices",
            "res_model": "account.move",
            "domain": [("patient_id", "=", self.id)],
            "context": {"default_patient_id": self.id},
            "view_mode": "tree,form",
            "target": "current",
        }

    def _compute_invoice_count(self):
        """NEW - COMPUTE - METHOD :That mrthod is use to count the
        number of total invoices"""
        for rec in self:
            invoice_count = self.env["account.move"].search_count(
                [("patient_id", "=", rec.id)]
            )
            rec.invoice_count = invoice_count
