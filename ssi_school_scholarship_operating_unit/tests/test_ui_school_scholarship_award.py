# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase -- NOT HttpCase. In 14.0, HttpCase does not set up
# cls.env in setUpClass, so fixtures written there would fail with
# AttributeError before the browser even starts.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiSchoolScholarshipAward(HttpSavepointCase):
    """Tour test for the Operating Unit auto-fill on
    ``school_scholarship_award`` create.
    """

    @classmethod
    def setUpClass(cls):
        """Create the master data required by the create tour.

        Grants ``admin`` the multi operating unit group (Pre-Condition
        IK: Operating Unit is gated by
        ``groups="operating_unit.group_multi_operating_unit"``), and
        creates a School with exactly one Operating Unit so this
        module's derivation has something unambiguous to fill in.
        """
        super().setUpClass()
        cls.user_admin = cls.env.ref("base.user_admin")
        cls.env.ref("operating_unit.group_multi_operating_unit").sudo().write(
            {"users": [(4, cls.user_admin.id)]}
        )

        ou_partner = cls.env["res.partner"].create(
            {"name": "TOUR OU Award Operating Unit Partner"}
        )
        cls.tour_operating_unit = cls.env["operating.unit"].create(
            {
                "name": "TOUR OU Award Operating Unit",
                "code": "TOUROUAW",
                "company_id": cls.env.ref("base.main_company").id,
                "partner_id": ou_partner.id,
            }
        )

        tour_grade_type = cls.env["school_grade_type"].create(
            {
                "name": "TOUR OU Award Grade Type",
                "code": "TOUROUAWGT",
            }
        )
        cls.tour_school = cls.env["school"].create(
            {
                "name": "TOUR OU Award School",
                "code": "TOUROUAWS",
                "grade_type_id": tour_grade_type.id,
                "operating_unit_ids": [(6, 0, [cls.tour_operating_unit.id])],
            }
        )
        tour_academic_year = cls.env["school_academic_year"].create(
            {
                "name": "TOUR OU Award Academic Year",
                "code": "TOUROUAWY",
                "date_start": "2026-07-01",
                "date_end": "2027-06-30",
            }
        )
        tour_academic_term = cls.env["school_academic_term"].create(
            {
                "name": "TOUR OU Award Academic Term",
                "code": "TOUROUAWTM",
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
                "year_id": tour_academic_year.id,
            }
        )
        tour_grade = cls.env["school_grade"].create(
            {
                "name": "TOUR OU Award Grade",
                "code": "TOUROUAWG",
                "type_id": tour_grade_type.id,
            }
        )
        tour_grade_class = cls.env["school_grade_class"].create(
            {
                "name": "TOUR OU Award Grade Class",
                "code": "TOUROUAWGC",
                "school_id": cls.tour_school.id,
                "grade_id": tour_grade.id,
            }
        )
        tour_contact = cls.env["res.partner"].create(
            {"name": "TOUR OU Award Student Contact"}
        )
        cls.tour_student = cls.env["school_student"].create(
            {
                "name": "TOUR OU Award Student",
                "code": "TOUROUAWST",
                "contact_id": tour_contact.id,
                "school_id": cls.tour_school.id,
            }
        )
        cls.tour_enrollment = cls.env["school_enrollment"].create(
            {
                # Manually assigned so the tour can pick this record
                # from the Enrollment m2o dropdown by typing
                # predictable text.
                "name": "TOUR-OU-AWARD-ENR-001",
                "academic_year_id": tour_academic_year.id,
                "academic_term_id": tour_academic_term.id,
                "school_id": cls.tour_school.id,
                "grade_id": tour_grade.id,
                "grade_class_id": tour_grade_class.id,
                "student_id": cls.tour_student.id,
            }
        )

        account_type_income = cls.env.ref("account.data_account_type_revenue")
        tour_journal = cls.env["account.journal"].create(
            {
                "name": "TOUR OU Award Sale Journal",
                "code": "TOUROUAWJ",
                "type": "sale",
            }
        )
        tour_discount_account = cls.env["account.account"].create(
            {
                "name": "TOUR OU Award Discount Account",
                "code": "TOUROUAWA",
                "user_type_id": account_type_income.id,
                "reconcile": False,
            }
        )
        tour_type = cls.env["school_scholarship_type"].create(
            {
                "name": "TOUR OU Award Scholarship Type",
                "code": "TOUROUAWT",
                "deduction_journal_id": tour_journal.id,
                "discount_account_id": tour_discount_account.id,
            }
        )
        tour_analytic_account = cls.env["account.analytic.account"].create(
            {"name": "TOUR OU Award Analytic"}
        )
        tour_funding_source = cls.env["school_scholarship_funding_source"].create(
            {
                "name": "TOUR OU Award Funding Source",
                "code": "TOUROUAWF",
                "analytic_account_id": tour_analytic_account.id,
            }
        )
        tour_product = cls.env["product.product"].create(
            {
                "name": "TOUR OU Award Product",
                "type": "service",
            }
        )
        cls.tour_program = cls.env["school_scholarship_program"].create(
            {
                "name": "TOUR OU Award Program",
                "code": "TOUROUAWPRG",
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
        Post-Condition" delta)
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_operating_unit_school_scholarship_award_create",
            login="admin",
        )
