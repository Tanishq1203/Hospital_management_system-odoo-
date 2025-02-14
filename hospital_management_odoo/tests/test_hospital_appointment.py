from odoo.tests.common import TransactionCase
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError, UserError


class TestHospitalAppointment(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestHospitalAppointment, cls).setUpClass()
        # Create a partner for the patient
        partner = cls.env["res.partner"].create(
            {
                "name": "abc",
            }
        )

        # Create new record for testing
        cls.patient = cls.env["hospital.patient"].create(
            {
                "name": "Test Patient",
                "age": 30,
                "gender": "male",
            }
        )

        cls.doctor = cls.env["hospital.doctor"].create(
            {
                "doctor_name": "Test Doctor",
            }
        )

        cls.appointment = cls.env["hospital.appointment"].create(
            {
                "patient_id": cls.patient.id,
                "doctor_id": cls.doctor.id,
                "date_appointment": date.today(),
                "date_checkup": datetime.now() + timedelta(days=1),
            }
        )

    def test_create_appointment(self):
        # Create new appointment in draft stage
        self.assertEqual(self.appointment.state, "draft")
        self.assertEqual(self.appointment.patient_id, self.patient)
        self.assertEqual(self.appointment.doctor_id, self.doctor)

    def test_action_confirm(self):
        # Change appointment stage from draft to confirm
        self.appointment.action_confirm()
        self.assertEqual(self.appointment.state, "confirm")

    def test_action_done(self):
        # Change the stage of appointment from confirm to done and create a bill
        self.appointment.action_confirm()
        self.appointment.action_done()
        self.assertEqual(self.appointment.state, "done")

        # Verify that the bill has been generated automatically
        generated_bill = self.env["account.move"].search(
            [("patient_id", "=", self.patient.patient_id)], limit=1
        )
        self.assertIsNotNone(
            generated_bill,
            "Bill should be generated automatically when appointment is marked as done",
        )
        self.assertEqual(
            generated_bill.patient_id,
            self.patient.patient_id.id,
            "Generated bill should be linked to the patient",
        )

    def test_action_cancel(self):
        # Change the stage of appointment to cancel
        self.appointment.action_confirm()
        self.appointment.action_cancel()
        self.assertEqual(self.appointment.state, "cancel")

    @classmethod
    def tearDownClass(cls):
        # Clean up any resources if needed
        super(TestHospitalAppointment, cls).tearDownClass()
