# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase -- NOT HttpCase. In 14.0, HttpCase does not set up
# cls.env in setUpClass, so fixtures written there would fail with
# AttributeError before the browser even starts.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiSchoolScholarshipAwardCreateDueDeduction(HttpSavepointCase):
    """Tour test for the Create Due Deduction work instruction, added
    to ``school_scholarship_award`` by this glue module.
    """

    @classmethod
    def setUpClass(cls):
        """Create an Award with one due, invoiced Schedule line."""
        super().setUpClass()
        admin = cls.env.ref("base.user_admin")
        account_type_income = cls.env.ref("account.data_account_type_revenue")
        account_type_receivable = cls.env.ref("account.data_account_type_receivable")

        # Pre-Condition -- School/Academic Year/Grade/Grade
        # Class/Student, so an Enrollment can be created for the tour
        # Student.
        tour_grade_type = cls.env["school_grade_type"].create(
            {
                "name": "TOUR CDD Grade Type",
                "code": "TOURCDDGT",
            }
        )
        tour_school = cls.env["school"].create(
            {
                "name": "TOUR CDD School",
                "code": "TOURCDDS",
                "grade_type_id": tour_grade_type.id,
            }
        )
        tour_academic_year = cls.env["school_academic_year"].create(
            {
                "name": "TOUR CDD Academic Year",
                "code": "TOURCDDY",
                "date_start": "2026-07-01",
                "date_end": "2027-06-30",
            }
        )
        tour_academic_term = cls.env["school_academic_term"].create(
            {
                "name": "TOUR CDD Academic Term",
                "code": "TOURCDDTM",
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
                "year_id": tour_academic_year.id,
                # Required before the enrollment using this term can
                # ever reach "open" --
                # school_enrollment._check_enrollment_window rejects
                # opening an enrollment whose term is not itself open
                # for enrollment.
                "enrollment_state": "open",
            }
        )
        tour_grade = cls.env["school_grade"].create(
            {
                "name": "TOUR CDD Grade",
                "code": "TOURCDDG",
                "type_id": tour_grade_type.id,
            }
        )
        tour_grade_class = cls.env["school_grade_class"].create(
            {
                "name": "TOUR CDD Grade Class",
                "code": "TOURCDDGC",
                "school_id": tour_school.id,
                "grade_id": tour_grade.id,
            }
        )
        tour_contact = cls.env["res.partner"].create(
            {
                "name": "TOUR CDD Student Contact",
            }
        )
        tour_student = cls.env["school_student"].create(
            {
                "name": "TOUR CDD Student",
                "code": "TOURCDDST",
                "contact_id": tour_contact.id,
                "school_id": tour_school.id,
            }
        )
        tour_enrollment = cls.env["school_enrollment"].create(
            {
                "name": "TOUR-CDD-ENR-001",
                "academic_year_id": tour_academic_year.id,
                "academic_term_id": tour_academic_term.id,
                "school_id": tour_school.id,
                "grade_id": tour_grade.id,
                "grade_class_id": tour_grade_class.id,
                "student_id": tour_student.id,
            }
        )
        # Confirm/Approve so payment_term._compute_state can ever read
        # "invoiced" -- it only does so once its own enrollment_id.state
        # is "open" or "done" (odoo-school-scholarship,
        # school_enrollment_payment_term.py, _compute_state). Run as
        # admin for both steps, mirroring ssi_school's own
        # test_data_enrollment_create_due_invoice.yaml.
        tour_enrollment.with_user(admin).action_confirm()
        tour_enrollment.invalidate_cache()
        tour_enrollment.with_user(admin).action_approve_approval()

        # Pre-Condition -- a Funding Source, a Product, and a Program
        # with one Fee Reduction Scope line, so the Award's Benefit
        # and Funding tabs both have something to select.
        tour_analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "TOUR CDD Analytic",
            }
        )
        tour_funding_source = cls.env["school_scholarship_funding_source"].create(
            {
                "name": "TOUR CDD Funding Source",
                "code": "TOURCDDF",
                "analytic_account_id": tour_analytic_account.id,
            }
        )
        tour_product = cls.env["product.product"].create(
            {
                "name": "TOUR CDD Product",
                "type": "service",
            }
        )
        tour_journal = cls.env["account.journal"].create(
            {
                "name": "TOUR CDD Sale Journal",
                "code": "TCDDJ",
                "type": "sale",
            }
        )
        tour_receivable_account = cls.env["account.account"].create(
            {
                "name": "TOUR CDD Receivable Account",
                "code": "TOURCDDRA",
                "user_type_id": account_type_receivable.id,
                "reconcile": True,
            }
        )
        tour_discount_account = cls.env["account.account"].create(
            {
                "name": "TOUR CDD Discount Account",
                "code": "TOURCDDDA",
                "user_type_id": account_type_income.id,
                "reconcile": False,
            }
        )
        tour_income_account = cls.env["account.account"].create(
            {
                "name": "TOUR CDD Income Account",
                "code": "TOURCDDIA",
                "user_type_id": account_type_income.id,
                "reconcile": False,
            }
        )
        tour_invoice_type = cls.env["customer_invoice_type"].create(
            {
                "name": "TOUR CDD Invoice Type",
                "code": "/",
                "journal_id": tour_journal.id,
                "receivable_account_id": tour_receivable_account.id,
            }
        )
        tour_type = cls.env["school_scholarship_type"].create(
            {
                "name": "TOUR CDD Scholarship Type",
                "code": "TOURCDDTY",
                "deduction_journal_id": tour_journal.id,
                "discount_account_id": tour_discount_account.id,
            }
        )
        tour_program = cls.env["school_scholarship_program"].create(
            {
                "name": "TOUR CDD Program",
                "code": "TOURCDDPRG",
                "type_id": tour_type.id,
                "school_id": tour_school.id,
                "academic_year_id": tour_academic_year.id,
                "funding_source_ids": [(6, 0, [tour_funding_source.id])],
                "deduction_journal_id": tour_journal.id,
                "discount_account_id": tour_discount_account.id,
                "scope_ids": [
                    (
                        0,
                        0,
                        {
                            "scope_basis": "product",
                            "product_id": tour_product.id,
                            "benefit_type": "fee_reduction",
                            "computation": "percentage",
                            "percentage": 40.0,
                        },
                    )
                ],
            }
        )

        # Pre-Condition -- one Payment Term already invoiced and open,
        # so its own Schedule line is due.
        tour_term = cls.env["school_enrollment_payment_term"].create(
            {
                "enrollment_id": tour_enrollment.id,
                "name": "TOUR CDD Term",
                "date_invoice": "2026-08-01",
                "detail_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": tour_product.id,
                            "name": "TOUR CDD Term Fee",
                            "account_id": tour_income_account.id,
                            "uom_quantity": 1.0,
                            "uom_id": cls.env.ref("uom.product_uom_unit").id,
                            "price_unit": 1000000.0,
                        },
                    )
                ],
            }
        )
        tour_invoice = cls.env["customer_invoice"].create(
            {
                "name": "TOUR-CDD-INV-001",
                "type_id": tour_invoice_type.id,
                "partner_id": tour_contact.id,
                "date": "2026-08-01",
                "date_due": "2026-08-15",
                "currency_id": cls.env.company.currency_id.id,
                "journal_id": tour_journal.id,
                "receivable_account_id": tour_receivable_account.id,
                "user_id": admin.id,
            }
        )
        # Without a Line, ``move_id`` is never created and
        # ``customer_invoice._20_skip_open`` jumps this document
        # straight from Confirm to Done -- it never stops at Open at
        # all (odoo-school-scholarship-deduction PR #25 CI finding).
        cls.env["customer_invoice.line"].create(
            {
                "customer_invoice_id": tour_invoice.id,
                "name": "TOUR CDD Invoice Line",
                "account_id": tour_income_account.id,
                "uom_quantity": 1,
                "price_unit": 1000000.0,
            }
        )
        tour_invoice.action_confirm()
        tour_invoice.invalidate_cache()
        tour_invoice.with_user(admin).action_approve_approval()
        tour_term.write({"customer_invoice_id": tour_invoice.id})

        # Pre-Condition -- the Award whose form the tour opens, with a
        # Fee Reduction Benefit line matching TOUR CDD Product, and a
        # Funding line at 100%.
        cls.tour_award = cls.env["school_scholarship_award"].create(
            {
                "name": "TOUR-AWARD-CREATEDEDUCTION-001",
                "program_id": tour_program.id,
                "student_id": tour_student.id,
                "enrollment_id": tour_enrollment.id,
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
                "discount_account_id": tour_discount_account.id,
                "deduction_journal_id": tour_journal.id,
                "user_id": admin.id,
                "benefit_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "TOUR CDD Benefit",
                            "product_id": tour_product.id,
                            "percentage": 40.0,
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
        # Create Due Deduction button's own policy requires
        # (create_deduction_ok) -- which also auto-generates one
        # Schedule line for the Term above via the award's own
        # post_open hook (_10_generate_schedule), so no manual
        # Schedule create() is needed here.
        cls.tour_award.action_confirm()
        cls.tour_award.invalidate_cache()
        cls.tour_award.with_user(admin).action_approve_approval()

    def test_create_due_deduction(self):
        """Run the create due deduction tour for ``school_scholarship_award``.

        IK: docs/school_scholarship_award/07-create-due-deduction.md
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_deduction_school_scholarship_award_create_due_deduction",
            login="admin",
        )
