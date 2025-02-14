from odoo import http
from odoo.http import request


class HospitalController(http.Controller):

    # @http.route("/hospital/patients", auth="public", website=True)
    # def HospitalPatient(self, **kwargs):
    #     return request.render("jyot_hospital_management.patient_page", {})

    @http.route('/hospital/patient/', website=True, auth='user')
    def hospital_patient(self, **kw):
        # return "Thanks for watching"
        patients = request.env['hospital.patient'].sudo().search([])
        return request.render("jyot_hospital_management.patients_page", {
            'patients': patients
        })
