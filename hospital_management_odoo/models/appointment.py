# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date


class HospitalAppointment(models.Model):
    """New Class : That containt methods and fields related
    hospital appointment"""

    _name = "hospital.appointment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Hospital Appointment"
    _order = "doctor_id,name,age"
    _rec_name = "patient_id"
    _rec_name_search = ["patient_id", "reference"]

    name = fields.Char(
        string="Order Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _("New"),
    )
    reference = fields.Char(string="Reference", default="New")
    patient_id = fields.Many2one(
        comodel_name="hospital.patient", string="Patient", required=True
    )

    age = fields.Integer(
        string="Age", related="patient_id.age", tracking=True, store=True
    )
    doctor_id = fields.Many2one(
        comodel_name="hospital.doctor", string="Doctor", required=True
    )
    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        string="Gender",
    )
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
    note = fields.Text(string="Description")
    date_appointment = fields.Date(string="Date")
    date_checkup = fields.Datetime(string="Check Up Time")
    prescription = fields.Text(string="Prescription")
    prescription_line_ids = fields.One2many(
        comodel_name="appointment.prescription.lines",
        inverse_name="appointment_id",
        string="Prescription Lines",
    )

    invoice_count = fields.Integer(
        string="Invoice Count", compute="_compute_invoice_count"
    )
    tags = fields.Many2many(comodel_name="hospital.tags", string="Tags")

    # ------------------------------------------
    # --------------BUTTONS-ACTIONS-------------
    # ------------------------------------------
    def action_confirm(self):
        """New Method : Use to confirm the appointment."""
        self.state = "confirm"

    def action_done(self):
        """New Method : Use to mark appointment as done.
        And also create bill for the appointment."""
        for rec in self:
            self.state = "done"
            self.create_invoice()
        return {
            "effect": {
                "fadeout": "slow",
                "message": "Check Invoice It's Ready",
                "type": "rainbow_man",
            }  # Return the rainbow man effect on done stage.
        }

    def action_draft(self):
        """New Method : Use to change appointment state as draft."""
        self.state = "draft"

    def action_cancel(self):
        """New Method : Use to cancel the appointment."""
        self.state = "cancel"

    # -------------------------------------
    # ------------constrains---------------
    # -------------------------------------

    @api.constrains("date_appointment")
    def _check_date_appointment(self):
        # check that the date is must be today or future not past date
        for record in self:
            if record.date_appointment and record.date_appointment < date.today():
                raise ValidationError(
                    "The appointment date must be today or in the future."
                )

    @api.constrains("date_checkup")
    def _check_date_checkup(self):
        # check time is must be in  future not in past
        for record in self:
            if record.date_checkup and record.date_checkup <= datetime.utcnow():
                raise ValidationError("The check-up time must be in the future.")

    # -------------------------------------
    # ------------ORM-METHODS--------------
    # -------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", ("New")) == ("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "hospital.appointment"
                ) or ("New")
        return super(HospitalAppointment, self).create(vals_list)

    def unlink(self):
        if self.state == "done":
            raise ValidationError(
                _("You Cannot Delete %s as it is in Done State" % self.name)
            )
        return super(HospitalAppointment, self).unlink()

    @api.onchange("patient_id")  # Decorators
    def onchange_patient_id(self):
        if self.patient_id:
            self.gender = getattr(
                self.patient_id, "gender", ""
            )  # [getattr] Access an attribute of an object dynamically
            self.note = getattr(
                self.patient_id, "note", ""
            )  # [getattr] Access an attribute of an object dynamically
        else:
            self.gender = ""
            self.note = ""

    # -------------------------------------------------
    # URL-ACTION [TO REDIRECT TO SPECIFIC TARGETED URL]
    # -------------------------------------------------

    def action_url(self):
        return {
            "type": "ir.actions.act_url",
            "target": "self",
            "url": "https://bizzappdev.com/%s/" % self.prescription,
        }

    def create_invoice(self):
        """New Method : create new invoice and redirect into account_move model
        which is inherited from account"""
        invoice_vals = {
            "move_type": "out_invoice",
            "partner_id": self.patient_id.id,
            "invoice_line_ids": [
                (
                    0,
                    0,
                    {
                        "name": "Appointment Fee",
                        "quantity": 1,
                        "price_unit": 100.0,  # Add line in every bill
                    },
                )
            ],
            "date": fields.Date.today(),
            "patient_id": self.patient_id.id,
            "doctor_id": self.doctor_id.id,
        }
        invoice = self.env["account.move"].create(invoice_vals)
        invoice.action_post()
        self.message_post(
            body=_("Invoice %s has been created for this appointment." % invoice.name)
        )

    def _compute_invoice_count(self):
        """Compute Method : use to count invoice count for appointment"""
        for rec in self:
            invoice_count = self.env["account.move"].search_count(
                [("patient_id", "=", rec.id)]
            )
            rec.invoice_count = invoice_count

    def action_open_invoice(self):
        # Search for the invoice related to this appointment
        invoice = self.env["account.move"].search(
            [
                (
                    "patient_id",
                    "=",
                    self.patient_id.id,
                ),
                ("state", "!=", "draft"),
            ],
            limit=1,
        )

        if invoice:
            return {
                "type": "ir.actions.act_window",
                "name": "Invoice",
                "res_model": "account.move",
                "res_id": invoice.id,
                "view_mode": "form",
                "view_type": "form",
                "target": "current",  # Opens in the same window
            }
        else:
            raise UserError(_("No invoice found for this appointment."))


class AppointmentPrescriptionLines(models.Model):
    # New Class : Contain the fields and logical mrthods related to appointment lines
    _name = "appointment.prescription.lines"
    _description = "Appointment Prescription Lines"

    name = fields.Char(string="Medicine", required=True)
    qty = fields.Integer(string="Quantity")
    appointment_id = fields.Many2one(
        comodel_name="hospital.appointment", string="Appointment", required=True
    )  # Ensure this field exists


class Appointment(models.Model):
    # Inherited class : Contain scheduled job and notification logic
    _inherit = "hospital.appointment"

    @api.model
    def send_appointment_reminders(self):
        appointments = self.search(
            [("date_appointment", "=", fields.Datetime.now().date())]
        )
        for appointment in appointments:
            template = self.env.ref(
                "jyot_hospital_management.email_template_appointment_reminder"
            )
            self.env["mail.template"].browse(template.id).send_mail(
                appointment.id, force_send=True
            )

    @api.model
    def notify_upcoming_appointments(self):
        upcoming_appointments = self.search(
            [("date_appointment", "<=", fields.Datetime.now() + timedelta(days=1))]
        )
        for appointment in upcoming_appointments:
            appointment.patient_id.message_post(
                body="Reminder: You have an upcoming appointment on %s"
                % appointment.date_appointment
            )

    # @api.model
    # def _rec_name_search(
    #     self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    # ):
    #     if not args:
    #         args = []
    #     if name:
    #         args = [
    #             "|",
    #             ("patient_id", operator, name),
    #             ("reference", operator, name),
    #         ] + args
    #     return self._search(args, limit=limit, access_rights_uid=name_get_uid)
    # [Note : By implementing _rec_name_search this way, you allow users to
    # search for hospital appointments
    # by either the patient ID or the reference, providing a flexible
    # search experience. used in methods like name_get and name_search of the ORM]
