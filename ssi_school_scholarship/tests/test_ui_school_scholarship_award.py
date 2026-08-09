# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase -- NOT HttpCase. In 14.0, HttpCase does not set up
# cls.env in setUpClass, so fixtures written there would fail with
# AttributeError before the browser even starts.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiSchoolScholarshipAward(HttpSavepointCase):
    """Tour tests for the ``school_scholarship_award`` work
    instructions.
    """

    @classmethod
    def setUpClass(cls):
        """Create the master data and awards required by the tours."""
        super().setUpClass()
        admin = cls.env.ref("base.user_admin")

        # Pre-Condition -- a Scholarship Type, so the Program's onchange
        # has something to default its accounting fields from.
        account_type_income = cls.env.ref("account.data_account_type_revenue")
        tour_journal = cls.env["account.journal"].create(
            {
                "name": "TOUR Award Sale Journal",
                "code": "TAWJ",
                "type": "sale",
            }
        )
        tour_discount_account = cls.env["account.account"].create(
            {
                "name": "TOUR Award Discount Account",
                "code": "TOURAWA",
                "user_type_id": account_type_income.id,
                "reconcile": False,
            }
        )
        tour_type = cls.env["school_scholarship_type"].create(
            {
                "name": "TOUR Award Scholarship Type",
                "code": "TOURAWT",
                "deduction_journal_id": tour_journal.id,
                "discount_account_id": tour_discount_account.id,
            }
        )

        # Pre-Condition -- School/Academic Year/Grade/Grade Class/Student,
        # so an Enrollment can be created for the tour Student.
        tour_grade_type = cls.env["school_grade_type"].create(
            {
                "name": "TOUR Award Grade Type",
                "code": "TOURAWGT",
            }
        )
        tour_school = cls.env["school"].create(
            {
                "name": "TOUR Award School",
                "code": "TOURAWS",
                "grade_type_id": tour_grade_type.id,
            }
        )
        tour_academic_year = cls.env["school_academic_year"].create(
            {
                "name": "TOUR Award Academic Year",
                "code": "TOURAWY",
                "date_start": "2026-07-01",
                "date_end": "2027-06-30",
            }
        )
        tour_academic_term = cls.env["school_academic_term"].create(
            {
                "name": "TOUR Award Academic Term",
                "code": "TOURAWTM",
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
                "year_id": tour_academic_year.id,
            }
        )
        tour_grade = cls.env["school_grade"].create(
            {
                "name": "TOUR Award Grade",
                "code": "TOURAWG",
                "type_id": tour_grade_type.id,
            }
        )
        tour_grade_class = cls.env["school_grade_class"].create(
            {
                "name": "TOUR Award Grade Class",
                "code": "TOURAWGC",
                "school_id": tour_school.id,
                "grade_id": tour_grade.id,
            }
        )
        tour_contact = cls.env["res.partner"].create(
            {
                "name": "TOUR Award Student Contact",
            }
        )
        cls.tour_student = cls.env["school_student"].create(
            {
                "name": "TOUR Award Student",
                "code": "TOURAWST",
                "contact_id": tour_contact.id,
                "school_id": tour_school.id,
            }
        )
        cls.tour_enrollment = cls.env["school_enrollment"].create(
            {
                # Manually assigned (rather than left as "/") so the
                # tour can pick this record from the Enrollment m2o
                # dropdown by typing predictable text -- the default
                # "*<id>" fallback name is not known at authoring time.
                "name": "TOUR-AWARD-ENR-001",
                "academic_year_id": tour_academic_year.id,
                "academic_term_id": tour_academic_term.id,
                "school_id": tour_school.id,
                "grade_id": tour_grade.id,
                "grade_class_id": tour_grade_class.id,
                "student_id": cls.tour_student.id,
            }
        )

        # Pre-Condition -- a Funding Source and a Product, plus a
        # Program with one Scope line, so the award's Benefit/Funding
        # tabs both have something to select.
        tour_analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "TOUR Award Analytic",
            }
        )
        cls.tour_funding_source = cls.env["school_scholarship_funding_source"].create(
            {
                "name": "TOUR Award Funding Source",
                "code": "TOURAWF",
                "analytic_account_id": tour_analytic_account.id,
            }
        )
        cls.tour_product = cls.env["product.product"].create(
            {
                "name": "TOUR Award Product",
                "type": "service",
            }
        )
        cls.tour_program = cls.env["school_scholarship_program"].create(
            {
                "name": "TOUR Award Program",
                "code": "TOURAWPRG",
                "type_id": tour_type.id,
                "school_id": tour_school.id,
                "academic_year_id": tour_academic_year.id,
                "funding_source_ids": [(6, 0, [cls.tour_funding_source.id])],
                "deduction_journal_id": tour_journal.id,
                "discount_account_id": tour_discount_account.id,
                "scope_ids": [
                    (
                        0,
                        0,
                        {
                            "scope_basis": "product",
                            "product_id": cls.tour_product.id,
                            "benefit_type": "fee_reduction",
                            "computation": "percentage",
                            "percentage": 40.0,
                        },
                    )
                ],
            }
        )

        # Pre-Condition for 04-confirm -- a Draft award with one Benefit
        # and one Funding line at 100%, so Confirm has something valid
        # to work on.
        cls.tour_award_confirm = cls.env["school_scholarship_award"].create(
            {
                # Manually assigned, for the same reason as the
                # Enrollment above: identifies this exact row in the
                # Scholarship Awards list, since three fixture awards
                # here otherwise share the same Student/Program.
                "name": "TOUR-AWARD-CONFIRM-001",
                "program_id": cls.tour_program.id,
                "student_id": cls.tour_student.id,
                "enrollment_id": cls.tour_enrollment.id,
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
                "benefit_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "TOUR Award Confirm Benefit",
                            "product_id": cls.tour_product.id,
                            "price_unit": 1000000.0,
                        },
                    )
                ],
                "funding_ids": [
                    (
                        0,
                        0,
                        {
                            "funding_source_id": cls.tour_funding_source.id,
                            "percentage": 100.0,
                        },
                    )
                ],
            }
        )

        # Pre-Condition for 05-approve -- the same as above, but already
        # pushed to Waiting for Approval in Python via
        # ``action_confirm()``, since Confirm itself is exercised by
        # 04-confirm.md's own tour.
        cls.tour_award_approve = cls.env["school_scholarship_award"].create(
            {
                "name": "TOUR-AWARD-APPROVE-001",
                "program_id": cls.tour_program.id,
                "student_id": cls.tour_student.id,
                "enrollment_id": cls.tour_enrollment.id,
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
                "benefit_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "TOUR Award Approve Benefit",
                            "product_id": cls.tour_product.id,
                            "price_unit": 1000000.0,
                        },
                    )
                ],
                "funding_ids": [
                    (
                        0,
                        0,
                        {
                            "funding_source_id": cls.tour_funding_source.id,
                            "percentage": 100.0,
                        },
                    )
                ],
            }
        )
        cls.tour_award_approve.action_confirm()

        # Pre-Condition for 10-cancel -- a Draft award, plus the
        # Cancellation Reason the wizard requires.
        cls.tour_award_cancel = cls.env["school_scholarship_award"].create(
            {
                "name": "TOUR-AWARD-CANCEL-001",
                "program_id": cls.tour_program.id,
                "student_id": cls.tour_student.id,
                "enrollment_id": cls.tour_enrollment.id,
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
            }
        )
        cls.env["base.cancel_reason"].create(
            {
                "name": "TOUR Award Cancel Reason",
            }
        )

        # ``mixin.transaction`` internal_user_rule filters by
        # ``user_id``, so every award used ``as_user: base.user_admin``
        # by a tour must be owned by admin -- fixtures are otherwise
        # created as SUPERUSER, which record rules never match
        # (odoo-development-ui-test, structure-and-runner.md, Fixture
        # berjalan sebagai SUPERUSER).
        (cls.tour_award_confirm | cls.tour_award_approve | cls.tour_award_cancel).write(
            {"user_id": admin.id}
        )

    def test_create(self):
        """Run the create tour for ``school_scholarship_award``.

        IK: docs/school_scholarship_award/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_school_scholarship_award_create",
            login="admin",
        )

    def test_confirm(self):
        """Run the confirm tour for ``school_scholarship_award``.

        IK: docs/school_scholarship_award/04-confirm.md
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_school_scholarship_award_confirm",
            login="admin",
        )

    def test_approve(self):
        """Run the approve tour for ``school_scholarship_award``.

        IK: docs/school_scholarship_award/05-approve.md
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_school_scholarship_award_approve",
            login="admin",
        )

    def test_cancel(self):
        """Run the cancel tour for ``school_scholarship_award``.

        IK: docs/school_scholarship_award/10-cancel.md
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_school_scholarship_award_cancel",
            login="admin",
        )
