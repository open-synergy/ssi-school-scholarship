# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolStudent(YamlTransactionCase):
    """Scenario tests for the scholarship fields glued onto
    ``school_student``.
    """

    def test_school_student_scholarship(self):
        """Run the scholarship visibility compute scenarios."""
        self.run_yaml_scenario("test_data_school_student.yaml")

    def test_open_scholarship_award_action(self):
        """The smart button returns an act_window scoped to this student.

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
        contact = self.env["res.partner"].create({"name": "P1 Contact"})
        student = self.env["school_student"].create(
            {
                "name": "P1 Student",
                "code": "/",
                "contact_id": contact.id,
                "school_id": school.id,
            }
        )
        action = student.action_open_scholarship_award()
        self.assertEqual(action["res_model"], "school_scholarship_award")
        self.assertEqual(action["domain"], [("student_id", "=", student.id)])
