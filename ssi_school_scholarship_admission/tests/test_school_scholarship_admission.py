# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolScholarshipAdmission(
    YamlTransactionCase
):  # pylint: disable=too-few-public-methods
    """Cover the Admission billing source for the scholarship core models.

    Covers ``school_scholarship_award`` creation with Billing Source
    Admission (School/Grade/Student derivation, Schedule generation
    against ``school_admission_payment_term``), the
    ``admission_id``/``student_id`` onchange, ``school_admission``'s
    Scholarship Amount/Count, the Enrollment path regression, and every
    Admission-specific negative path.
    """

    def test_school_scholarship_admission(self):
        """Run every scholarship Admission billing source scenario."""
        self.run_yaml_scenario("test_data_school_scholarship_admission.yaml")

    def test_open_scholarship_award_action(self):
        """The smart button returns an act_window scoped to this
        admission.

        P1, L-01/L-02: ``action: call`` discards the method's return
        value and the YAML ``assert`` action's *actual* side is
        always a dotted ``getattr`` on a record, so the returned
        ``ir.actions.act_window`` dict has to be inspected here, in
        plain Python.
        """
        grade_type = self.env["school_grade_type"].create(
            {
                "name": "P1 ADM Grade Type",
                "code": "/",
            }
        )
        school = self.env["school"].create(
            {
                "name": "P1 ADM School",
                "code": "/",
                "grade_type_id": grade_type.id,
            }
        )
        academic_year = self.env["school_academic_year"].create(
            {
                "name": "P1 ADM Academic Year",
                "code": "/",
                "date_start": "2026-07-01",
                "date_end": "2027-06-30",
            }
        )
        academic_term = self.env["school_academic_term"].create(
            {
                "name": "P1 ADM Term",
                "code": "/",
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
                "year_id": academic_year.id,
            }
        )
        grade = self.env["school_grade"].create(
            {
                "name": "P1 ADM Grade",
                "code": "/",
                "type_id": grade_type.id,
            }
        )
        contact = self.env["res.partner"].create({"name": "P1 ADM Contact"})
        admission = self.env["school_admission"].create(
            {
                "academic_year_id": academic_year.id,
                "academic_term_id": academic_term.id,
                "school_id": school.id,
                "grade_id": grade.id,
                "student_id": contact.id,
            }
        )
        action = admission.action_open_scholarship_award()
        self.assertEqual(action["res_model"], "school_scholarship_award")
        self.assertEqual(action["domain"], [("admission_id", "=", admission.id)])
