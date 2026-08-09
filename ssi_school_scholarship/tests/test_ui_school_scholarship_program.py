# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase -- NOT HttpCase. In 14.0, HttpCase does not set up
# cls.env in setUpClass, so fixtures written there would fail with
# AttributeError before the browser even starts.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiSchoolScholarshipProgram(HttpSavepointCase):
    """Tour tests for the ``school_scholarship_program`` work
    instructions.
    """

    @classmethod
    def setUpClass(cls):
        """Create the records and configuration required by the tour."""
        super().setUpClass()
        account_type_income = cls.env.ref("account.data_account_type_revenue")

        # Pre-Condition -- a Scholarship Type whose accounting fields are
        # valid, so the onchange(type_id) it triggers does not leave the
        # required Deduction Journal / Discount Account fields empty.
        tour_journal = cls.env["account.journal"].create(
            {
                "name": "TOUR Program Sale Journal",
                "code": "TOURPRGJ",
                "type": "sale",
            }
        )
        tour_discount_account = cls.env["account.account"].create(
            {
                "name": "TOUR Program Discount Account",
                "code": "TOURPRGA",
                "user_type_id": account_type_income.id,
                "reconcile": False,
            }
        )
        cls.tour_type = cls.env["school_scholarship_type"].create(
            {
                "name": "TOUR Program Scholarship Type",
                "code": "TOURPRGT",
                "deduction_journal_id": tour_journal.id,
                "discount_account_id": tour_discount_account.id,
            }
        )

        # Pre-Condition -- a School (with its required Grade Type) and an
        # Academic Year, picked from the m2o dropdown by their unique
        # names.
        tour_grade_type = cls.env["school_grade_type"].create(
            {
                "name": "TOUR Program Grade Type",
                "code": "TOURPRGGT",
            }
        )
        cls.tour_school = cls.env["school"].create(
            {
                "name": "TOUR Program School",
                "code": "TOURPRGS",
                "grade_type_id": tour_grade_type.id,
            }
        )
        cls.tour_academic_year = cls.env["school_academic_year"].create(
            {
                "name": "TOUR Program Academic Year",
                "code": "TOURPRGY",
                "date_start": "2026-07-01",
                "date_end": "2027-06-30",
            }
        )

        # Pre-Condition -- a Funding Source, picked from the m2m tag
        # dropdown by its unique name.
        tour_analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "TOUR Program Analytic",
            }
        )
        cls.tour_funding_source = cls.env["school_scholarship_funding_source"].create(
            {
                "name": "TOUR Program Funding Source",
                "code": "TOURPRGF",
                "analytic_account_id": tour_analytic_account.id,
            }
        )

        # Pre-Condition for Generate Code (docs/school_scholarship_program/
        # 01-create.md, Flow 7): an active sequence.template for this
        # model is required, or clicking the button raises a UserError
        # instead of assigning a code.
        cls.code_sequence = cls.env["ir.sequence"].create(
            {
                "name": "TOUR Program Code Sequence",
                "code": "ssi_school_scholarship.tour.school_scholarship_program",
                "prefix": "TOURSEQPRG",
                "padding": 4,
            }
        )
        cls.code_sequence_template = cls.env["sequence.template"].create(
            {
                "name": "TOUR Program Sequence Template",
                "model_id": cls.env["ir.model"]._get_id("school_scholarship_program"),
                "sequence_field_id": cls.env["ir.model.fields"]
                ._get("school_scholarship_program", "code")
                .id,
                "date_field_id": cls.env["ir.model.fields"]
                ._get("school_scholarship_program", "create_date")
                .id,
                "sequence_selection_method": "use_sequence",
                "sequence_id": cls.code_sequence.id,
            }
        )

    def test_create(self):
        """Run the create tour for ``school_scholarship_program``.

        IK: docs/school_scholarship_program/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_school_scholarship_program_create",
            login="admin",
        )
