# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolScholarshipAwardCreateDueDeduction(YamlTransactionCase):
    """Scenario tests for the Create Due Deduction feature added to
    ``school_scholarship_award`` by this glue module -- grouping by
    invoice, skipping not-yet-due Schedule lines, idempotency once a
    Deduction opens, and the wizard's own multi-Award and negative
    paths.
    """

    def test_award_create_due_deduction(self):
        """Run the create due deduction scenario.

        Covers ``_get_due_schedule``/``_create_due_deduction`` on the
        Award, and the ``create_due_scholarship_deduction`` wizard's
        multi-Award and negative (``UserError``) paths.
        """
        self.run_yaml_scenario(
            "test_data_school_scholarship_award_create_due_deduction.yaml"
        )

    def test_action_open_create_due_deduction_wizard_returns_action(self):
        """Assert the action dict returned when opening the wizard.

        Pure Python -- trigger P1 (L-01: ``action: call`` discards the
        method's return value, and L-02: the "actual" side of every
        YAML assert is always a ``getattr`` on a record, never a bare
        dict). Run against a recordset of *two* Awards -- rather than
        one -- to also demonstrate that ``active_ids`` carries every
        selected Award, the same code path exercised when the button
        is clicked from several rows selected in the list view.
        """
        grade_type = self.env["school_grade_type"].create(
            {
                "name": "P1 Grade Type",
                "code": "P1GT",
            }
        )
        school = self.env["school"].create(
            {
                "name": "P1 School",
                "code": "P1SC",
                "grade_type_id": grade_type.id,
            }
        )
        academic_year = self.env["school_academic_year"].create(
            {
                "name": "P1 Academic Year",
                "code": "P1AY",
                "date_start": "2026-07-01",
                "date_end": "2027-06-30",
            }
        )
        academic_term = self.env["school_academic_term"].create(
            {
                "name": "P1 Academic Term",
                "code": "P1TM",
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
                "year_id": academic_year.id,
            }
        )
        grade = self.env["school_grade"].create(
            {
                "name": "P1 Grade",
                "code": "P1GR",
                "type_id": grade_type.id,
            }
        )
        grade_class = self.env["school_grade_class"].create(
            {
                "name": "P1 Grade Class",
                "code": "P1CL",
                "school_id": school.id,
                "grade_id": grade.id,
            }
        )
        contact = self.env["res.partner"].create(
            {
                "name": "P1 Contact",
            }
        )
        student = self.env["school_student"].create(
            {
                "name": "P1 Student",
                "code": "P1ST",
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
        account_type_income = self.env.ref("account.data_account_type_revenue")
        discount_account = self.env["account.account"].create(
            {
                "name": "P1 Discount Account",
                "code": "P1DA",
                "user_type_id": account_type_income.id,
                "reconcile": False,
            }
        )
        journal = self.env["account.journal"].create(
            {
                "name": "P1 Journal",
                "code": "JP1",
                "type": "sale",
            }
        )
        scholarship_type = self.env["school_scholarship_type"].create(
            {
                "name": "P1 Type",
                "code": "P1TY",
                "deduction_journal_id": journal.id,
                "discount_account_id": discount_account.id,
            }
        )
        product = self.env["product.product"].create(
            {
                "name": "P1 Product",
                "type": "service",
            }
        )
        # ``scope_ids`` is required -- an empty Program fails
        # ``_check_scope_ids`` (forced explicitly in ``create()`` even
        # when this key is entirely absent from ``vals``).
        program = self.env["school_scholarship_program"].create(
            {
                "name": "P1 Program",
                "code": "P1PRG",
                "type_id": scholarship_type.id,
                "school_id": school.id,
                "academic_year_id": academic_year.id,
                "deduction_journal_id": journal.id,
                "discount_account_id": discount_account.id,
                "scope_ids": [
                    (
                        0,
                        0,
                        {
                            "scope_basis": "product",
                            "product_id": product.id,
                            "benefit_type": "fee_reduction",
                            "computation": "percentage",
                            "percentage": 40.0,
                        },
                    )
                ],
            }
        )
        award_1 = self.env["school_scholarship_award"].create(
            {
                "program_id": program.id,
                "student_id": student.id,
                "enrollment_id": enrollment.id,
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
            }
        )
        award_2 = self.env["school_scholarship_award"].create(
            {
                "program_id": program.id,
                "student_id": student.id,
                "enrollment_id": enrollment.id,
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
            }
        )
        awards = award_1 | award_2

        # ``bypass_policy_check`` skips ``create_deduction_ok`` -- that
        # policy gate is exercised by the wizard's own negative-path
        # scenario in YAML; this method only asserts the shape of the
        # returned action dict.
        action = awards.with_context(
            bypass_policy_check=True
        ).action_open_create_due_deduction_wizard()

        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["target"], "new")
        self.assertEqual(action["res_model"], "create_due_scholarship_deduction")
        self.assertEqual(sorted(action["context"]["active_ids"]), sorted(awards.ids))
