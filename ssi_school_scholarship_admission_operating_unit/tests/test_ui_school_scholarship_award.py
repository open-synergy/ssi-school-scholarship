# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase -- NOT HttpCase. In 14.0, HttpCase does not set up
# cls.env in setUpClass, so fixtures written there would fail with
# AttributeError before the browser even starts.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiSchoolScholarshipAward(HttpSavepointCase):
    """Tour test for the Operating Unit auto-fill on an Admission-sourced
    ``school_scholarship_award`` create.
    """

    @classmethod
    def setUpClass(cls):
        """Create the master data required by the create tour.

        Every record the tour types into an m2o must already exist,
        since a miss silently turns the pick step into a
        record-creation dialog: a Program, a School Student for base
        IK Flow 3, and an Admission for the
        ``ssi_school_scholarship_admission`` delta. Also grants
        ``admin`` the multi operating unit group (Pre-Condition IK:
        Operating Unit is gated by
        ``groups="operating_unit.group_multi_operating_unit"``), and
        the Admission's School carries exactly one Operating Unit so
        this module's derivation has something unambiguous to fill in.

        The Admission is progressed to Open (Confirm then Approve) so
        it satisfies the Admission field's own domain
        (``state in ('open', 'done')``) -- the tour picks it from the
        m2o dropdown by typing its manually assigned ``name``.
        """
        super().setUpClass()
        cls.user_admin = cls.env.ref("base.user_admin")
        cls.env.ref("operating_unit.group_multi_operating_unit").sudo().write(
            {"users": [(4, cls.user_admin.id)]}
        )

        ou_partner = cls.env["res.partner"].create(
            {"name": "TOUR ADMOU Award Operating Unit Partner"}
        )
        cls.tour_operating_unit = cls.env["operating.unit"].create(
            {
                "name": "TOUR ADMOU Award Operating Unit",
                "code": "TOURADMOU",
                "company_id": cls.env.ref("base.main_company").id,
                "partner_id": ou_partner.id,
            }
        )

        tour_grade_type = cls.env["school_grade_type"].create(
            {
                "name": "TOUR ADMOU Award Grade Type",
                "code": "TOURADMOUGT",
            }
        )
        cls.tour_school = cls.env["school"].create(
            {
                "name": "TOUR ADMOU Award School",
                "code": "TOURADMOUS",
                "grade_type_id": tour_grade_type.id,
                "operating_unit_ids": [(6, 0, [cls.tour_operating_unit.id])],
            }
        )
        tour_academic_year = cls.env["school_academic_year"].create(
            {
                "name": "TOUR ADMOU Award Academic Year",
                "code": "TOURADMOUY",
                "date_start": "2026-07-01",
                "date_end": "2027-06-30",
            }
        )
        tour_academic_term = cls.env["school_academic_term"].create(
            {
                "name": "TOUR ADMOU Award Academic Term",
                "code": "TOURADMOUTM",
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
                "year_id": tour_academic_year.id,
            }
        )
        tour_grade = cls.env["school_grade"].create(
            {
                "name": "TOUR ADMOU Award Grade",
                "code": "TOURADMOUG",
                "type_id": tour_grade_type.id,
            }
        )
        tour_admission_student_contact = cls.env["res.partner"].create(
            {"name": "TOUR ADMOU Award Admission Student"}
        )

        # Base IK Flow 3 has the user pick a Student before the Billing
        # Source delta, so a School Student carrying exactly the text
        # the tour types must EXIST. Without it the m2o dropdown offers
        # only its "Create ..." entries, the pick step matches one of
        # those, and -- because school_student requires contact_id and
        # school_id -- the quick create fails and Odoo falls back to
        # the full "Create: Student" dialog. Every later step then
        # searches inside that modal (web_tour scopes triggers to the
        # visible modal) and times out on a form field that is in fact
        # rendered correctly underneath.
        tour_award_student_contact = cls.env["res.partner"].create(
            {"name": "TOUR ADMOU Award Student Contact"}
        )
        cls.tour_student = cls.env["school_student"].create(
            {
                "name": "TOUR ADMOU Award Student",
                "code": "TOURADMOUST",
                "contact_id": tour_award_student_contact.id,
                "school_id": cls.tour_school.id,
            }
        )

        cls.tour_admission = cls.env["school_admission"].create(
            {
                # Manually assigned so the tour can pick this record
                # from the Admission m2o dropdown by typing
                # predictable text.
                "name": "TOUR-ADMOU-AWARD-ADM-001",
                "academic_year_id": tour_academic_year.id,
                "academic_term_id": tour_academic_term.id,
                "school_id": cls.tour_school.id,
                "grade_id": tour_grade.id,
                "student_id": tour_admission_student_contact.id,
                # setUpClass runs as SUPERUSER, so without this the
                # record would be owned by superuser and record rule
                # school_admission_internal_user_rule
                # ([('user_id','=',user.id)]) would hide it from the
                # tour's own session, which logs in as admin -- the m2o
                # dropdown would simply never offer it.
                "user_id": cls.user_admin.id,
            }
        )
        # Advancing the fixture past its policy gate is Pre-Condition
        # setup, not the behaviour under test: the tour asserts the
        # award form, and it only needs an Admission already Open (so
        # school_student_id exists and the Admission field's domain
        # accepts it). Calling the transitions bare would fail on
        # approve_ok, which one shared compute caches as False while
        # action_confirm reads confirm_ok with state still Draft
        # (odoo-development-unit-test, test-traps.md T-04). Same
        # helper shape as ssi_school_scholarship_admission's own tour
        # fixture.
        bypass = cls.tour_admission.with_context(bypass_policy_check=True)
        bypass.action_confirm()
        bypass.action_approve_approval()

        account_type_income = cls.env.ref("account.data_account_type_revenue")
        tour_journal = cls.env["account.journal"].create(
            {
                "name": "TOUR ADMOU Award Sale Journal",
                "code": "TOURADMOUJ",
                "type": "sale",
            }
        )
        tour_discount_account = cls.env["account.account"].create(
            {
                "name": "TOUR ADMOU Award Discount Account",
                "code": "TOURADMOUA",
                "user_type_id": account_type_income.id,
                "reconcile": False,
            }
        )
        tour_type = cls.env["school_scholarship_type"].create(
            {
                "name": "TOUR ADMOU Award Scholarship Type",
                "code": "TOURADMOUT",
                "deduction_journal_id": tour_journal.id,
                "discount_account_id": tour_discount_account.id,
            }
        )
        tour_analytic_account = cls.env["account.analytic.account"].create(
            {"name": "TOUR ADMOU Award Analytic"}
        )
        tour_funding_source = cls.env["school_scholarship_funding_source"].create(
            {
                "name": "TOUR ADMOU Award Funding Source",
                "code": "TOURADMOUF",
                "analytic_account_id": tour_analytic_account.id,
            }
        )
        tour_product = cls.env["product.product"].create(
            {
                "name": "TOUR ADMOU Award Product",
                "type": "service",
            }
        )
        cls.tour_program = cls.env["school_scholarship_program"].create(
            {
                "name": "TOUR ADMOU Award Program",
                "code": "TOURADMOUPRG",
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
        """Run the create tour for an Admission-sourced
        ``school_scholarship_award``.

        IK: docs/school_scholarship_award/01-create.md ("Additional
        Post-Condition" delta)
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_admission_operating_unit_school_scholarship_award_create",
            login="admin",
        )
