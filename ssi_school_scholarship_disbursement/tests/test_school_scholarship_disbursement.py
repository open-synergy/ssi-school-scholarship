# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolScholarshipDisbursement(YamlTransactionCase):
    """Scenario tests for ``school_scholarship_disbursement``."""

    def test_school_scholarship_disbursement(self):
        """Run the compute, workflow, reconcile, and negative path
        scenarios.

        :return: nothing
        """
        self.run_yaml_scenario("test_data_school_scholarship_disbursement.yaml")

    def test_get_due_cash_schedule_filters_fee_reduction(self):
        """``_get_due_cash_schedule`` must return only Cash lines.

        Built directly in Python (P1: nilai balik method; L-01/L-02,
        odoo-development-unit-test references/python-escape-hatch.md)
        because ``action: call`` in the YAML DSL discards a method's
        return value, and this method's return value -- which of two
        Schedule lines it selected -- is exactly what is under test.
        The Award carries one Fee Reduction Benefit line (its own
        Schedule line requires a Payment Term) and one Cash Benefit
        line (its own Schedule line must not carry one), both
        ``scheduled``.
        """
        grade_type = self.env["school_grade_type"].create(
            {"name": "E1 Grade Type", "code": "E1GT"}
        )
        school = self.env["school"].create(
            {
                "name": "E1 School",
                "code": "E1SC",
                "grade_type_id": grade_type.id,
            }
        )
        academic_year = self.env["school_academic_year"].create(
            {
                "name": "E1 Academic Year",
                "code": "E1AY",
                "date_start": "2026-07-01",
                "date_end": "2027-06-30",
            }
        )
        academic_term = self.env["school_academic_term"].create(
            {
                "name": "E1 Term",
                "code": "E1TM",
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
                "year_id": academic_year.id,
            }
        )
        grade = self.env["school_grade"].create(
            {"name": "E1 Grade", "code": "E1GR", "type_id": grade_type.id}
        )
        grade_class = self.env["school_grade_class"].create(
            {
                "name": "E1 Class",
                "code": "E1CL",
                "school_id": school.id,
                "grade_id": grade.id,
            }
        )
        contact = self.env["res.partner"].create({"name": "E1 Contact"})
        student = self.env["school_student"].create(
            {
                "name": "E1 Student",
                "code": "E1ST",
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
        analytic_account = self.env["account.analytic.account"].create(
            {"name": "E1 Analytic"}
        )
        funding_source = self.env["school_scholarship_funding_source"].create(
            {
                "name": "E1 Funding Source",
                "code": "E1FS",
                "analytic_account_id": analytic_account.id,
            }
        )
        product = self.env["product.product"].create(
            {"name": "E1 Product", "type": "service"}
        )
        deduction_journal = self.env["account.journal"].create(
            {"name": "E1 Deduction Journal", "code": "E1DJ", "type": "sale"}
        )
        account_type_income = self.env.ref("account.data_account_type_revenue")
        discount_account = self.env["account.account"].create(
            {
                "name": "E1 Discount Account",
                "code": "E1DA",
                "user_type_id": account_type_income.id,
                "reconcile": False,
            }
        )
        scholarship_type = self.env["school_scholarship_type"].create(
            {
                "name": "E1 Type",
                "code": "E1TY",
                "deduction_journal_id": deduction_journal.id,
                "discount_account_id": discount_account.id,
            }
        )
        program = self.env["school_scholarship_program"].create(
            {
                "name": "E1 Program",
                "code": "E1PRG",
                "type_id": scholarship_type.id,
                "school_id": school.id,
                "academic_year_id": academic_year.id,
                "funding_source_ids": [(6, 0, [funding_source.id])],
                "deduction_journal_id": deduction_journal.id,
                "discount_account_id": discount_account.id,
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
                "benefit_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "E1 Fee Reduction Benefit",
                            "product_id": product.id,
                            "benefit_type": "fee_reduction",
                            "computation": "fixed",
                            "amount_fixed": 100000.0,
                            "periodicity": "per_payment_term",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "E1 Cash Benefit",
                            "product_id": product.id,
                            "benefit_type": "cash",
                            "computation": "fixed",
                            "amount_fixed": 500000.0,
                            "periodicity": "one_time",
                        },
                    ),
                ],
            }
        )
        fee_reduction_benefit = award.benefit_ids.filtered(
            lambda benefit: benefit.benefit_type == "fee_reduction"
        )
        cash_benefit = award.benefit_ids.filtered(
            lambda benefit: benefit.benefit_type == "cash"
        )
        payment_term = self.env["school_enrollment_payment_term"].create(
            {
                "enrollment_id": enrollment.id,
                "name": "E1 Payment Term",
                "sequence": 5,
            }
        )
        fee_reduction_schedule = self.env["school_scholarship_award_schedule"].create(
            {
                "benefit_id": fee_reduction_benefit.id,
                "payment_term_id": payment_term.id,
                "date": "2026-08-01",
                "state": "scheduled",
            }
        )
        cash_schedule = self.env["school_scholarship_award_schedule"].create(
            {
                "benefit_id": cash_benefit.id,
                "date": "2026-08-01",
                "state": "scheduled",
            }
        )

        result = award._get_due_cash_schedule()

        self.assertEqual(result, cash_schedule)
        self.assertNotIn(fee_reduction_schedule, result)

    def test_insert_form_element_view_element_disabled(self):
        """``_insert_form_element`` must skip the statusbar
        reconfiguration when ``_automatically_insert_view_element``
        is falsy.

        That attribute is a hardcoded ``True`` class constant on this
        model (mirroring the toggle ``mixin.transaction`` itself
        defaults to ``False``), so no business flow can ever reach
        the ``False`` branch on this concrete model -- exercised
        directly with ``mock.patch.object`` instead (P6: mock/patch;
        L-15, odoo-development-unit-test
        references/python-escape-hatch.md).
        """
        disbursement = self.env["school_scholarship_disbursement"]
        view_arch = "<form><header/></form>"
        with mock.patch.object(
            type(disbursement), "_automatically_insert_view_element", False
        ):
            result = disbursement._insert_form_element(view_arch)
        self.assertEqual(result, view_arch)
