# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.exceptions import UserError
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolScholarshipDeductionRecognition(YamlTransactionCase):
    """Scenario tests for ``school_scholarship_deduction_recognition``."""

    def test_school_scholarship_deduction_recognition(self):
        """Run the compute, workflow, and asymmetry guard scenarios."""
        self.run_yaml_scenario(
            "test_data_school_scholarship_deduction_recognition.yaml"
        )

    def test_wizard_create_due_recognition(self):
        """``create_due_scholarship_recognition`` releases a due deduction.

        Pure Python -- trigger P1 (L-01: ``action_create_due_recognition``
        returns an ``ir.actions.act_window`` dict, which the YAML DSL's
        ``call`` action would discard; L-02: the same holds for
        ``default_get``/``onchange_deduction_ids``'s own effect on
        ``deduction_ids``, which ``action: call`` cannot observe
        either), odoo-development-unit-test
        references/python-escape-hatch.md.
        """
        admin = self.env.ref("base.user_admin")
        grade_type = self.env["school_grade_type"].create(
            {"name": "WZ Grade Type", "code": "WZGT"}
        )
        school = self.env["school"].create(
            {"name": "WZ School", "code": "WZSC", "grade_type_id": grade_type.id}
        )
        academic_year = self.env["school_academic_year"].create(
            {
                "name": "WZ Academic Year",
                "code": "WZAY",
                "date_start": "2026-07-01",
                "date_end": "2027-06-30",
            }
        )
        contact = self.env["res.partner"].create({"name": "WZ Contact"})
        student = self.env["school_student"].create(
            {
                "name": "WZ Student",
                "code": "WZST",
                "contact_id": contact.id,
                "school_id": school.id,
            }
        )
        academic_term = self.env["school_academic_term"].create(
            {
                "name": "WZ Term",
                "code": "WZTM",
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
                "year_id": academic_year.id,
            }
        )
        grade = self.env["school_grade"].create(
            {"name": "WZ Grade", "code": "WZGR", "type_id": grade_type.id}
        )
        grade_class = self.env["school_grade_class"].create(
            {
                "name": "WZ Class",
                "code": "WZCL",
                "school_id": school.id,
                "grade_id": grade.id,
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
        analytic = self.env["account.analytic.account"].create({"name": "WZ Analytic"})
        funding_source = self.env["school_scholarship_funding_source"].create(
            {
                "name": "WZ Funding Source",
                "code": "WZFS",
                "analytic_account_id": analytic.id,
            }
        )
        product = self.env["product.product"].create(
            {"name": "WZ Product", "type": "service"}
        )
        journal = self.env["account.journal"].create(
            {"name": "WZ Journal", "code": "WZJ", "type": "sale"}
        )
        account_type_income = self.env.ref("account.data_account_type_revenue")
        account_type_asset = self.env.ref("account.data_account_type_current_assets")
        account_type_receivable = self.env.ref("account.data_account_type_receivable")
        receivable_account = self.env["account.account"].create(
            {
                "name": "WZ Receivable Account",
                "code": "WZRA",
                "user_type_id": account_type_receivable.id,
                "reconcile": True,
            }
        )
        discount_account = self.env["account.account"].create(
            {
                "name": "WZ Discount Account",
                "code": "WZDA",
                "user_type_id": account_type_income.id,
                "reconcile": False,
            }
        )
        deferred_account = self.env["account.account"].create(
            {
                "name": "WZ Deferred Account",
                "code": "WZFA",
                "user_type_id": account_type_asset.id,
                "reconcile": False,
            }
        )
        scholarship_type = self.env["school_scholarship_type"].create(
            {
                "name": "WZ Type",
                "code": "WZTY",
                "deduction_journal_id": journal.id,
                "discount_account_id": discount_account.id,
            }
        )
        program = self.env["school_scholarship_program"].create(
            {
                "name": "WZ Program",
                "code": "WZPRG",
                "type_id": scholarship_type.id,
                "school_id": school.id,
                "academic_year_id": academic_year.id,
                "funding_source_ids": [(6, 0, [funding_source.id])],
                "deduction_journal_id": journal.id,
                "discount_account_id": discount_account.id,
                "allow_asymmetric_recognition": True,
                "scope_ids": [
                    (
                        0,
                        0,
                        {
                            "scope_basis": "product",
                            "product_id": product.id,
                            "benefit_type": "cash",
                            "computation": "fixed",
                            "amount_fixed": 100000.0,
                        },
                    )
                ],
            }
        )
        award = self.env["school_scholarship_award"].create(
            {
                "program_id": program.id,
                "student_id": student.id,
                "enrollment_id": enrollment.id,
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
                "deferred_discount_account_id": deferred_account.id,
                "recognition_journal_id": journal.id,
                "benefit_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "WZ Benefit",
                            "product_id": product.id,
                            "benefit_type": "cash",
                            "computation": "fixed",
                            "amount_fixed": 400000.0,
                            "periodicity": "one_time",
                        },
                    )
                ],
                "funding_ids": [
                    (
                        0,
                        0,
                        {
                            "funding_source_id": funding_source.id,
                            "percentage": 100.0,
                        },
                    )
                ],
            }
        )
        benefit = award.benefit_ids[:1]
        funding = award.funding_ids[:1]
        schedule = self.env["school_scholarship_award_schedule"].create(
            {
                "benefit_id": benefit.id,
                "date": "2026-08-01",
                "state": "scheduled",
            }
        )
        deduction = self.env["school_scholarship_deduction"].create(
            {
                "award_id": award.id,
                "date": "2026-03-01",
                "journal_id": journal.id,
                "receivable_account_id": receivable_account.id,
                "deferred_account_id": deferred_account.id,
                "recognition_journal_id": journal.id,
                "user_id": admin.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "schedule_id": schedule.id,
                            "funding_id": funding.id,
                            "final_account_id": discount_account.id,
                            "name": "WZ Deduction Line",
                            "uom_quantity": 1,
                            "price_unit": 400000.0,
                        },
                    )
                ],
            }
        )
        self.assertEqual(deduction.recognition_state, "pending")

        wizard = self.env["create_due_scholarship_recognition"].create(
            {"date": "2026-09-01"}
        )
        wizard.onchange_deduction_ids()
        self.assertIn(deduction.id, wizard.deduction_ids.ids)

        action = wizard.action_create_due_recognition()
        self.assertEqual(
            action["res_model"], "school_scholarship_deduction_recognition"
        )
        recognition = self.env["school_scholarship_deduction_recognition"].search(
            [("deduction_id", "=", deduction.id)]
        )
        self.assertEqual(len(recognition), 1)
        self.assertEqual(recognition.amount, 400000.0)

    def test_wizard_create_due_recognition_no_deduction(self):
        """``_check_deduction_ids`` rejects an empty selection.

        Pure Python -- trigger P1 (L-01: ``action_create_due_recognition``
        returns an ``ir.actions.act_window`` dict / raises directly,
        neither of which ``action: call`` can assert on),
        odoo-development-unit-test references/python-escape-hatch.md.
        """
        wizard = self.env["create_due_scholarship_recognition"].create(
            {"date": "2026-09-01", "deduction_ids": [(5, 0, 0)]}
        )
        with self.assertRaises(UserError):
            wizard.action_create_due_recognition()
