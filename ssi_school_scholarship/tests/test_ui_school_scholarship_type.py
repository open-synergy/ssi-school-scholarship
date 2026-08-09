# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase -- NOT HttpCase. In 14.0, HttpCase does not set up
# cls.env in setUpClass, so fixtures written there would fail with
# AttributeError before the browser even starts.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiSchoolScholarshipType(HttpSavepointCase):
    """Tour tests for the ``school_scholarship_type`` work instructions."""

    @classmethod
    def setUpClass(cls):
        """Create the records and configuration required by the tour."""
        super().setUpClass()
        # Pre-Condition for the create tour (docs/school_scholarship_type/
        # 01-create.md): a Deduction Journal that is not Cash/Bank, and a
        # non-reconcilable Discount Account, both picked from the m2o
        # dropdown by their unique names.
        cls.tour_journal = cls.env["account.journal"].create(
            {
                "name": "TOUR Scholarship Sale Journal",
                "code": "TOURSCHJ1",
                "type": "sale",
            }
        )
        account_type_income = cls.env.ref("account.data_account_type_revenue")
        cls.tour_account = cls.env["account.account"].create(
            {
                "name": "TOUR Scholarship Discount Account",
                "code": "TOURSCHA1",
                "user_type_id": account_type_income.id,
                "reconcile": False,
            }
        )

        # Pre-Condition for Generate Code (docs/school_scholarship_type/
        # 01-create.md, Flow 7): an active sequence.template for this
        # model is required, or clicking the button raises a UserError
        # instead of assigning a code.
        cls.code_sequence = cls.env["ir.sequence"].create(
            {
                "name": "TOUR Scholarship Type Code Sequence",
                "code": "ssi_school_scholarship.tour.school_scholarship_type",
                "prefix": "TOURSEQSCH",
                "padding": 4,
            }
        )
        cls.code_sequence_template = cls.env["sequence.template"].create(
            {
                "name": "TOUR Scholarship Type Sequence Template",
                "model_id": cls.env["ir.model"]._get_id("school_scholarship_type"),
                "sequence_field_id": cls.env["ir.model.fields"]
                ._get("school_scholarship_type", "code")
                .id,
                "date_field_id": cls.env["ir.model.fields"]
                ._get("school_scholarship_type", "create_date")
                .id,
                "sequence_selection_method": "use_sequence",
                "sequence_id": cls.code_sequence.id,
            }
        )

    def test_create(self):
        """Run the create tour for ``school_scholarship_type``.

        IK: docs/school_scholarship_type/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_school_scholarship_type_create",
            login="admin",
        )
