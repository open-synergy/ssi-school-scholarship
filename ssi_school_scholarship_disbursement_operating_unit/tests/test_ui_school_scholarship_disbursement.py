# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase -- NOT HttpCase. In 14.0, HttpCase does not set up
# cls.env in setUpClass, so fixtures written there would fail with
# AttributeError before the browser even starts.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiSchoolScholarshipDisbursement(HttpSavepointCase):
    """Tour test for the Operating Unit auto-fill on
    ``school_scholarship_disbursement`` create.
    """

    @classmethod
    def setUpClass(cls):
        """Create the master data required by the create tour.

        Grants ``admin`` the multi operating unit group (Pre-Condition
        IK: Operating Unit is gated by
        ``groups="operating_unit.group_multi_operating_unit"``), and
        creates a School with exactly one Operating Unit plus an Award
        of that School's Enrollment, so this module's own derivation
        (from the Award's Operating Unit) has something to fill in.
        """
        super().setUpClass()
        cls.user_admin = cls.env.ref("base.user_admin")
        cls.env.ref("operating_unit.group_multi_operating_unit").sudo().write(
            {"users": [(4, cls.user_admin.id)]}
        )

        ou_partner = cls.env["res.partner"].create(
            {"name": "TOUR Disbursement OU Operating Unit Partner"}
        )
        cls.tour_operating_unit = cls.env["operating.unit"].create(
            {
                "name": "TOUR Disbursement OU Operating Unit",
                "code": "TOURDBOU",
                "company_id": cls.env.ref("base.main_company").id,
                "partner_id": ou_partner.id,
            }
        )

        tour_grade_type = cls.env["school_grade_type"].create(
            {
                "name": "TOUR Disbursement OU Grade Type",
                "code": "TOURDBOUGT",
            }
        )
        cls.tour_school = cls.env["school"].create(
            {
                "name": "TOUR Disbursement OU School",
                "code": "TOURDBOUS",
                "grade_type_id": tour_grade_type.id,
                "operating_unit_ids": [(6, 0, [cls.tour_operating_unit.id])],
            }
        )
        tour_academic_year = cls.env["school_academic_year"].create(
            {
                "name": "TOUR Disbursement OU Academic Year",
                "code": "TOURDBOUY",
                "date_start": "2026-07-01",
                "date_end": "2027-06-30",
            }
        )
        tour_academic_term = cls.env["school_academic_term"].create(
            {
                "name": "TOUR Disbursement OU Academic Term",
                "code": "TOURDBOUTM",
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
                "year_id": tour_academic_year.id,
            }
        )
        tour_grade = cls.env["school_grade"].create(
            {
                "name": "TOUR Disbursement OU Grade",
                "code": "TOURDBOUG",
                "type_id": tour_grade_type.id,
            }
        )
        tour_grade_class = cls.env["school_grade_class"].create(
            {
                "name": "TOUR Disbursement OU Grade Class",
                "code": "TOURDBOUGC",
                "school_id": cls.tour_school.id,
                "grade_id": tour_grade.id,
            }
        )
        tour_contact = cls.env["res.partner"].create(
            {"name": "TOUR Disbursement OU Student Contact"}
        )
        cls.tour_student = cls.env["school_student"].create(
            {
                "name": "TOUR Disbursement OU Student",
                "code": "TOURDBOUST",
                "contact_id": tour_contact.id,
                "school_id": cls.tour_school.id,
            }
        )
        cls.tour_enrollment = cls.env["school_enrollment"].create(
            {
                "name": "TOUR-DISBURSEMENT-OU-ENR-001",
                "academic_year_id": tour_academic_year.id,
                "academic_term_id": tour_academic_term.id,
                "school_id": cls.tour_school.id,
                "grade_id": tour_grade.id,
                "grade_class_id": tour_grade_class.id,
                "student_id": cls.tour_student.id,
            }
        )

        account_type_income = cls.env.ref("account.data_account_type_revenue")
        account_type_expense = cls.env.ref("account.data_account_type_expenses")
        tour_dummy_journal = cls.env["account.journal"].create(
            {
                "name": "TOUR Disbursement OU Dummy Deduction Journal",
                "code": "TOURDBOUJD",
                "type": "sale",
            }
        )
        tour_discount_account = cls.env["account.account"].create(
            {
                "name": "TOUR Disbursement OU Discount Account",
                "code": "TOURDBOUDA",
                "user_type_id": account_type_income.id,
                "reconcile": False,
            }
        )
        tour_expense_account = cls.env["account.account"].create(
            {
                "name": "TOUR Disbursement OU Expense Account",
                "code": "TOURDBOUEA",
                "user_type_id": account_type_expense.id,
                "reconcile": False,
            }
        )
        tour_type = cls.env["school_scholarship_type"].create(
            {
                "name": "TOUR Disbursement OU Scholarship Type",
                "code": "TOURDBOUT",
                "deduction_journal_id": tour_dummy_journal.id,
                "discount_account_id": tour_discount_account.id,
            }
        )
        tour_analytic_account = cls.env["account.analytic.account"].create(
            {"name": "TOUR Disbursement OU Analytic"}
        )
        tour_funding_source = cls.env["school_scholarship_funding_source"].create(
            {
                "name": "TOUR Disbursement OU Funding Source",
                "code": "TOURDBOUF",
                "analytic_account_id": tour_analytic_account.id,
            }
        )
        tour_product = cls.env["product.product"].create(
            {
                "name": "TOUR Disbursement OU Product",
                "type": "service",
            }
        )
        cls.tour_program = cls.env["school_scholarship_program"].create(
            {
                "name": "TOUR Disbursement OU Program",
                "code": "TOURDBOUPRG",
                "type_id": tour_type.id,
                "school_id": cls.tour_school.id,
                "academic_year_id": tour_academic_year.id,
                "funding_source_ids": [(6, 0, [tour_funding_source.id])],
                "deduction_journal_id": tour_dummy_journal.id,
                "discount_account_id": tour_discount_account.id,
                "scope_ids": [
                    (
                        0,
                        0,
                        {
                            "scope_basis": "product",
                            "product_id": tour_product.id,
                            "benefit_type": "cash",
                            "computation": "fixed",
                            "amount_fixed": 500000.0,
                        },
                    )
                ],
            }
        )
        cls.tour_award = cls.env["school_scholarship_award"].create(
            {
                "name": "TOUR-DISBURSEMENT-OU-AWARD-001",
                "program_id": cls.tour_program.id,
                "student_id": cls.tour_student.id,
                "enrollment_id": cls.tour_enrollment.id,
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
                "expense_account_id": tour_expense_account.id,
                "benefit_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "TOUR Disbursement OU Benefit",
                            "product_id": tour_product.id,
                            "benefit_type": "cash",
                            "computation": "fixed",
                            "amount_fixed": 500000.0,
                            "periodicity": "one_time",
                        },
                    )
                ],
                "funding_ids": [
                    (
                        0,
                        0,
                        {
                            "funding_source_id": tour_funding_source.id,
                            "percentage": 100.0,
                        },
                    )
                ],
            }
        )

    def test_create(self):
        """Run the create tour for ``school_scholarship_disbursement``.

        IK: docs/school_scholarship_disbursement/01-create.md
        ("Additional Post-Condition" delta)
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_disbursement_operating_unit_school_scholarship_disbursement_create",  # noqa: B950
            login="admin",
        )
