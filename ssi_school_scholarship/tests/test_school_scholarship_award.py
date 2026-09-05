# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolScholarshipAward(YamlTransactionCase):
    """Scenario tests for ``school_scholarship_award``."""

    def test_school_scholarship_award(self):
        """Run the CRUD, workflow, onchange, and negative path scenarios."""
        self.run_yaml_scenario("test_data_school_scholarship_award.yaml")

    def test_insert_form_element_view_element_disabled(self):
        """``_insert_form_element`` must skip the statusbar
        reconfiguration when ``_automatically_insert_view_element``
        is falsy.

        That attribute is a hardcoded ``True`` class constant on this
        model (mirroring the toggle ``mixin.transaction`` itself
        defaults to ``False``), so no business flow can ever reach
        the ``False`` branch on this concrete model -- exercised
        directly with ``mock.patch.object`` instead. Pure Python --
        trigger P6 (L-15: odoo-yaml-test has no mock/patch support),
        odoo-development-unit-test references/python-escape-hatch.md.
        """
        award = self.env["school_scholarship_award"]
        view_arch = "<form><header/></form>"
        with mock.patch.object(
            type(award), "_automatically_insert_view_element", False
        ):
            result = award._insert_form_element(view_arch)
        self.assertEqual(result, view_arch)


@tagged("post_install", "-at_install")
class TestSchoolScholarshipAwardViewActions(YamlTransactionCase):
    """Tests for the ``action_view_schedule`` smart button actions.

    Fixture built here in Python, not via YAML -- these two actions
    only return an ``ir.actions.act_window`` dict, so asserting their
    ``domain``/``res_model`` is trigger P1 (L-01, L-02: a ``call``
    step in ``odoo-yaml-test`` discards a method's return value), and
    the pustaka's registry does not survive past ``run_yaml_scenario``
    for a later method to reuse (odoo-development-unit-test
    references/python-escape-hatch.md §4).
    """

    def setUp(self):
        """Build one award with 5 Schedule lines (2 realized), plus a
        second bare award used only for the ``ensure_one`` negative
        path.
        """
        super().setUp()
        grade_type = self.env["school_grade_type"].create(
            {"name": "AV Grade Type", "code": "AVGT"}
        )
        school = self.env["school"].create(
            {
                "name": "AV School",
                "code": "AVSC",
                "grade_type_id": grade_type.id,
            }
        )
        academic_year = self.env["school_academic_year"].create(
            {
                "name": "AV Academic Year",
                "code": "AVAY",
                "date_start": "2026-07-01",
                "date_end": "2027-06-30",
            }
        )
        academic_term = self.env["school_academic_term"].create(
            {
                "name": "AV Term",
                "code": "AVTM",
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
                "year_id": academic_year.id,
            }
        )
        grade = self.env["school_grade"].create(
            {"name": "AV Grade", "code": "AVGR", "type_id": grade_type.id}
        )
        grade_class = self.env["school_grade_class"].create(
            {
                "name": "AV Class",
                "code": "AVCL",
                "school_id": school.id,
                "grade_id": grade.id,
            }
        )
        contact = self.env["res.partner"].create({"name": "AV Contact"})
        student = self.env["school_student"].create(
            {
                "name": "AV Student",
                "code": "AVST",
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
        product = self.env["product.product"].create(
            {"name": "AV Product", "type": "service"}
        )
        journal = self.env["account.journal"].create(
            {"name": "AV Journal", "code": "JAV", "type": "sale"}
        )
        account_type_income = self.env.ref("account.data_account_type_revenue")
        discount_account = self.env["account.account"].create(
            {
                "name": "AV Discount Account",
                "code": "AVDA",
                "user_type_id": account_type_income.id,
                "reconcile": False,
            }
        )
        scholarship_type = self.env["school_scholarship_type"].create(
            {
                "name": "AV Type",
                "code": "AVTY",
                "deduction_journal_id": journal.id,
                "discount_account_id": discount_account.id,
            }
        )
        program = self.env["school_scholarship_program"].create(
            {
                "name": "AV Program",
                "code": "AVPRG",
                "type_id": scholarship_type.id,
                "school_id": school.id,
                "academic_year_id": academic_year.id,
                "deduction_journal_id": journal.id,
                "discount_account_id": discount_account.id,
            }
        )
        # 1 One Time line + 4 Monthly lines (Jul..Oct, one per month)
        # once generated -- see ``_get_cash_schedule_dates``.
        self.award = self.env["school_scholarship_award"].create(
            {
                "program_id": program.id,
                "student_id": student.id,
                "enrollment_id": enrollment.id,
                "date_start": "2026-07-01",
                "date_end": "2026-10-31",
                "benefit_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "AV Benefit One Time",
                            "product_id": product.id,
                            "benefit_type": "cash",
                            "computation": "fixed",
                            "amount_fixed": 100000.0,
                            "periodicity": "one_time",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "AV Benefit Monthly",
                            "product_id": product.id,
                            "benefit_type": "cash",
                            "computation": "fixed",
                            "amount_fixed": 50000.0,
                            "periodicity": "monthly",
                        },
                    ),
                ],
            }
        )
        self.award.with_context(bypass_policy_check=True)._generate_schedule()
        self.realized_schedules = self.award.schedule_ids[:2]
        self.realized_schedules.write({"state": "realized"})

        # A second, bare award (no Benefit line needed) purely to
        # form a 2-record recordset for the ``ensure_one`` check.
        self.other_award = self.env["school_scholarship_award"].create(
            {
                "program_id": program.id,
                "student_id": student.id,
                "enrollment_id": enrollment.id,
                "date_start": "2026-07-01",
                "date_end": "2026-07-31",
            }
        )

    def test_action_view_schedule_lists_all_lines(self):
        """``action_view_schedule`` opens all of this award's lines.

        Pure Python -- trigger P1 (L-01, L-02: the returned
        ``ir.actions.act_window`` dict cannot be asserted through
        ``odoo-yaml-test``'s ``call`` action).
        """
        action = self.award.action_view_schedule()
        self.assertEqual(action["res_model"], "school_scholarship_award_schedule")
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["domain"], [("award_id", "=", self.award.id)])
        found = self.env[action["res_model"]].search(action["domain"])
        self.assertEqual(found, self.award.schedule_ids)
        self.assertEqual(len(found), 5)

    def test_action_view_realized_schedule_lists_only_realized(self):
        """``action_view_realized_schedule`` opens only the Realized
        lines.

        Pure Python -- trigger P1 (L-01, L-02: same as
        ``test_action_view_schedule_lists_all_lines``).
        """
        action = self.award.action_view_realized_schedule()
        self.assertEqual(action["res_model"], "school_scholarship_award_schedule")
        self.assertEqual(
            action["domain"],
            [("award_id", "=", self.award.id), ("state", "=", "realized")],
        )
        found = self.env[action["res_model"]].search(action["domain"])
        self.assertEqual(found, self.realized_schedules)
        self.assertEqual(len(found), 2)

    def test_action_view_schedule_ensure_one_on_multiple_awards(self):
        """Calling either action on more than one award must fail.

        Pure Python -- trigger P1 (L-01, L-02: the failure mode of a
        method whose return value ``odoo-yaml-test`` cannot inspect
        is exercised the same way its success path is).
        """
        both_awards = self.award | self.other_award
        with self.assertRaises(ValueError):
            both_awards.action_view_schedule()
        with self.assertRaises(ValueError):
            both_awards.action_view_realized_schedule()
