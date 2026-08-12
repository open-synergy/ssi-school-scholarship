# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase -- NOT HttpCase. In 14.0, HttpCase does not set up
# cls.env in setUpClass, so fixtures written there would fail with
# AttributeError before the browser even starts.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiSchoolScholarshipAwardCreateDueDisbursement(HttpSavepointCase):
    """Tour test for the Create Due Disbursement work instruction, added
    to ``school_scholarship_award`` by this module.
    """

    @classmethod
    def setUpClass(cls):
        """Create an Award with one due Cash Schedule line."""
        super().setUpClass()
        admin = cls.env.ref("base.user_admin")
        account_type_income = cls.env.ref("account.data_account_type_revenue")
        account_type_payable = cls.env.ref("account.data_account_type_payable")
        account_type_expense = cls.env.ref("account.data_account_type_expenses")

        # Pre-Condition -- School/Academic Year/Grade/Grade
        # Class/Student, so an Enrollment can be created for the tour
        # Student.
        tour_grade_type = cls.env["school_grade_type"].create(
            {
                "name": "TOUR CDDB Grade Type",
                "code": "TOURCDDBGT",
            }
        )
        tour_school = cls.env["school"].create(
            {
                "name": "TOUR CDDB School",
                "code": "TOURCDDBS",
                "grade_type_id": tour_grade_type.id,
            }
        )
        tour_academic_year = cls.env["school_academic_year"].create(
            {
                "name": "TOUR CDDB Academic Year",
                "code": "TOURCDDBY",
                "date_start": "2026-07-01",
                "date_end": "2027-06-30",
            }
        )
        tour_academic_term = cls.env["school_academic_term"].create(
            {
                "name": "TOUR CDDB Academic Term",
                "code": "TOURCDDBTM",
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
                "year_id": tour_academic_year.id,
            }
        )
        tour_grade = cls.env["school_grade"].create(
            {
                "name": "TOUR CDDB Grade",
                "code": "TOURCDDBG",
                "type_id": tour_grade_type.id,
            }
        )
        tour_grade_class = cls.env["school_grade_class"].create(
            {
                "name": "TOUR CDDB Grade Class",
                "code": "TOURCDDBGC",
                "school_id": tour_school.id,
                "grade_id": tour_grade.id,
            }
        )
        tour_contact = cls.env["res.partner"].create(
            {
                "name": "TOUR CDDB Student Contact",
            }
        )
        tour_student = cls.env["school_student"].create(
            {
                "name": "TOUR CDDB Student",
                "code": "TOURCDDBST",
                "contact_id": tour_contact.id,
                "school_id": tour_school.id,
            }
        )
        tour_enrollment = cls.env["school_enrollment"].create(
            {
                "name": "TOUR-CDDB-ENR-001",
                "academic_year_id": tour_academic_year.id,
                "academic_term_id": tour_academic_term.id,
                "school_id": tour_school.id,
                "grade_id": tour_grade.id,
                "grade_class_id": tour_grade_class.id,
                "student_id": tour_student.id,
            }
        )

        # Pre-Condition -- a Funding Source, a Product, a Program with
        # one Cash Scope line, and a Journal/Payable/Expense account
        # trio, so the Award's Benefit and Funding tabs both have
        # something to select, and reaching Open auto-generates a due
        # Cash Schedule line.
        tour_analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "TOUR CDDB Analytic",
            }
        )
        tour_funding_source = cls.env["school_scholarship_funding_source"].create(
            {
                "name": "TOUR CDDB Funding Source",
                "code": "TOURCDDBF",
                "analytic_account_id": tour_analytic_account.id,
            }
        )
        tour_product = cls.env["product.product"].create(
            {
                "name": "TOUR CDDB Product",
                "type": "service",
            }
        )
        tour_journal = cls.env["account.journal"].create(
            {
                "name": "TOUR CDDB Cash Journal",
                "code": "TCDDBJ",
                "type": "cash",
            }
        )
        # school_scholarship_type/_program require a Deduction Journal
        # and Discount Account even though this tour never posts a
        # deduction -- a dummy sale journal + non-reconcilable income
        # account satisfies those two unrelated required fields.
        tour_dummy_journal = cls.env["account.journal"].create(
            {
                "name": "TOUR CDDB Dummy Deduction Journal",
                "code": "TCDDBJD",
                "type": "sale",
            }
        )
        tour_discount_account = cls.env["account.account"].create(
            {
                "name": "TOUR CDDB Discount Account",
                "code": "TOURCDDBDA",
                "user_type_id": account_type_income.id,
                "reconcile": False,
            }
        )
        tour_payable_account = cls.env["account.account"].create(
            {
                "name": "TOUR CDDB Payable Account",
                "code": "TOURCDDBPA",
                "user_type_id": account_type_payable.id,
                "reconcile": True,
            }
        )
        tour_expense_account = cls.env["account.account"].create(
            {
                "name": "TOUR CDDB Expense Account",
                "code": "TOURCDDBEA",
                "user_type_id": account_type_expense.id,
                "reconcile": False,
            }
        )
        tour_type = cls.env["school_scholarship_type"].create(
            {
                "name": "TOUR CDDB Scholarship Type",
                "code": "TOURCDDBTY",
                "deduction_journal_id": tour_dummy_journal.id,
                "discount_account_id": tour_discount_account.id,
                "disbursement_journal_id": tour_journal.id,
                "payable_account_id": tour_payable_account.id,
            }
        )
        tour_program = cls.env["school_scholarship_program"].create(
            {
                "name": "TOUR CDDB Program",
                "code": "TOURCDDBPRG",
                "type_id": tour_type.id,
                "school_id": tour_school.id,
                "academic_year_id": tour_academic_year.id,
                "funding_source_ids": [(6, 0, [tour_funding_source.id])],
                "deduction_journal_id": tour_dummy_journal.id,
                "discount_account_id": tour_discount_account.id,
                "disbursement_journal_id": tour_journal.id,
                "payable_account_id": tour_payable_account.id,
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

        # Pre-Condition -- the Award whose form the tour opens, with a
        # Cash Benefit line matching TOUR CDDB Product (periodicity
        # "one_time", so exactly one due Schedule line is generated at
        # the Award's own Date Start), and a Funding line at 100%.
        cls.tour_award = cls.env["school_scholarship_award"].create(
            {
                "name": "TOUR-AWARD-CREATEDISBURSEMENT-001",
                "program_id": tour_program.id,
                "student_id": tour_student.id,
                "enrollment_id": tour_enrollment.id,
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
                # school_scholarship_award_benefit._compute_account_id
                # reads this directly off the Award (not through any
                # onchange chain) for a Benefit with benefit_type
                # "cash", as created below. create() here never runs
                # the form's own onchange_expense_account_id (that
                # only fires in the real web client), so without this
                # the Benefit's own account_id -- and, through the
                # disbursement Line's onchange_final_account_id, the
                # disbursement Line's own Final Account -- would
                # compute to False.
                "expense_account_id": tour_expense_account.id,
                "benefit_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "TOUR CDDB Benefit",
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
        # Confirm/Approve so the Award reaches Open -- the state the
        # Create Due Disbursement button's own Pre-Condition requires
        # -- which also auto-generates one due Cash Schedule line for
        # the Benefit above via the award's own post_open hook
        # (_10_generate_schedule -> _generate_cash_schedule), so no
        # manual Schedule create() is needed here.
        cls.tour_award.action_confirm()
        cls.tour_award.invalidate_cache()
        cls.tour_award.with_user(admin).action_approve_approval()

    def test_create_due_disbursement(self):
        """Run the create due disbursement tour for ``school_scholarship_award``.

        IK: docs/school_scholarship_award/08-create-due-disbursement.md
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_disbursement_school_scholarship_award_"
            "create_due_disbursement",
            login="admin",
        )
