# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase -- NOT HttpCase. In 14.0, HttpCase does not set up
# cls.env in setUpClass, so fixtures written there would fail with
# AttributeError before the browser even starts.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiSchoolScholarshipAward(HttpSavepointCase):
    """Tour test for the Admission Billing Source on ``school_scholarship_award``
    create.
    """

    @classmethod
    def setUpClass(cls):
        """Create the master data required by the create tour.

        Progresses the Admission to Open (Confirm then Approve) so it
        satisfies the Admission field's own domain
        (``state in ('open', 'done')``) -- the tour picks it from the
        m2o dropdown by typing its manually assigned ``name``.
        """
        super().setUpClass()
        cls.user_admin = cls.env.ref("base.user_admin")

        tour_grade_type = cls.env["school_grade_type"].create(
            {
                "name": "TOUR ADM Award Grade Type",
                "code": "TOURADMAWGT",
            }
        )
        cls.tour_school = cls.env["school"].create(
            {
                "name": "TOUR ADM Award School",
                "code": "TOURADMAWS",
                "grade_type_id": tour_grade_type.id,
            }
        )
        tour_academic_year = cls.env["school_academic_year"].create(
            {
                "name": "TOUR ADM Award Academic Year",
                "code": "TOURADMAWY",
                "date_start": "2026-07-01",
                "date_end": "2027-06-30",
            }
        )
        tour_academic_term = cls.env["school_academic_term"].create(
            {
                "name": "TOUR ADM Award Academic Term",
                "code": "TOURADMAWTM",
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
                "year_id": tour_academic_year.id,
            }
        )
        tour_grade = cls.env["school_grade"].create(
            {
                "name": "TOUR ADM Award Grade",
                "code": "TOURADMAWG",
                "type_id": tour_grade_type.id,
            }
        )
        tour_student_contact = cls.env["res.partner"].create(
            {"name": "TOUR ADM Award Admission Student"}
        )

        cls.tour_admission = cls.env["school_admission"].create(
            {
                # Manually assigned so the tour can pick this record
                # from the Admission m2o dropdown by typing
                # predictable text.
                "name": "TOUR-ADM-AWARD-ADM-001",
                "academic_year_id": tour_academic_year.id,
                "academic_term_id": tour_academic_term.id,
                "school_id": cls.tour_school.id,
                "grade_id": tour_grade.id,
                "student_id": tour_student_contact.id,
            }
        )
        cls.tour_admission.action_confirm()
        cls.tour_admission.action_approve_approval()

        account_type_income = cls.env.ref("account.data_account_type_revenue")
        tour_journal = cls.env["account.journal"].create(
            {
                "name": "TOUR ADM Award Sale Journal",
                "code": "TOURADMAWJ",
                "type": "sale",
            }
        )
        tour_discount_account = cls.env["account.account"].create(
            {
                "name": "TOUR ADM Award Discount Account",
                "code": "TOURADMAWA",
                "user_type_id": account_type_income.id,
                "reconcile": False,
            }
        )
        tour_type = cls.env["school_scholarship_type"].create(
            {
                "name": "TOUR ADM Award Scholarship Type",
                "code": "TOURADMAWT",
                "deduction_journal_id": tour_journal.id,
                "discount_account_id": tour_discount_account.id,
            }
        )
        tour_analytic_account = cls.env["account.analytic.account"].create(
            {"name": "TOUR ADM Award Analytic"}
        )
        tour_funding_source = cls.env["school_scholarship_funding_source"].create(
            {
                "name": "TOUR ADM Award Funding Source",
                "code": "TOURADMAWF",
                "analytic_account_id": tour_analytic_account.id,
            }
        )
        tour_product = cls.env["product.product"].create(
            {
                "name": "TOUR ADM Award Product",
                "type": "service",
            }
        )
        cls.tour_program = cls.env["school_scholarship_program"].create(
            {
                "name": "TOUR ADM Award Program",
                "code": "TOURADMAWPRG",
                "type_id": tour_type.id,
                "school_id": cls.tour_school.id,
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

    def test_create(self):
        """Run the create tour for ``school_scholarship_award``.

        IK: docs/school_scholarship_award/01-create.md ("Additional
        Fields" delta)
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_admission_school_scholarship_award_create",
            login="admin",
        )
