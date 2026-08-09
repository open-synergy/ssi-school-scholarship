# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolEnrollment(YamlTransactionCase):
    """Scenario tests for the scholarship fields glued onto
    ``school_enrollment``.
    """

    def test_school_enrollment_scholarship(self):
        """Run the scholarship amount compute scenario."""
        self.run_yaml_scenario("test_data_school_enrollment.yaml")

    def test_open_scholarship_award_action(self):
        """The smart button returns an act_window scoped to this
        enrollment.

        P1, L-01/L-02: ``action: call`` discards the method's return
        value and the YAML ``assert`` action's *actual* side is
        always a dotted ``getattr`` on a record, so the returned
        ``ir.actions.act_window`` dict has to be inspected here, in
        plain Python.
        """
        grade_type = self.env["school_grade_type"].create(
            {
                "name": "P1 Grade Type",
                "code": "/",
            }
        )
        school = self.env["school"].create(
            {
                "name": "P1 School",
                "code": "/",
                "grade_type_id": grade_type.id,
            }
        )
        academic_year = self.env["school_academic_year"].create(
            {
                "name": "P1 Academic Year",
                "code": "/",
                "date_start": "2026-07-01",
                "date_end": "2027-06-30",
            }
        )
        academic_term = self.env["school_academic_term"].create(
            {
                "name": "P1 Term",
                "code": "/",
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
                "year_id": academic_year.id,
            }
        )
        grade = self.env["school_grade"].create(
            {
                "name": "P1 Grade",
                "code": "/",
                "type_id": grade_type.id,
            }
        )
        grade_class = self.env["school_grade_class"].create(
            {
                "name": "P1 Class",
                "code": "/",
                "school_id": school.id,
                "grade_id": grade.id,
            }
        )
        contact = self.env["res.partner"].create({"name": "P1 Contact"})
        student = self.env["school_student"].create(
            {
                "name": "P1 Student",
                "code": "/",
                "contact_id": contact.id,
                "school_id": school.id,
            }
        )
        enrollment = self.env["school_enrollment"].create(
            {
                "academic_year_id": academic_year.id,
                "academic_term_id": academic_term.id,
                "school_id": school.id,
                "grade_id": grade.id,
                "grade_class_id": grade_class.id,
                "student_id": student.id,
            }
        )
        action = enrollment.action_open_scholarship_award()
        self.assertEqual(action["res_model"], "school_scholarship_award")
        self.assertEqual(action["domain"], [("enrollment_id", "=", enrollment.id)])
