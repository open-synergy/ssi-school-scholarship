# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase -- NOT HttpCase. In 14.0, HttpCase does not set up
# cls.env in setUpClass, so fixtures written there would fail with
# AttributeError before the browser even starts.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiSchoolScholarshipFundingSource(HttpSavepointCase):
    """Tour tests for the ``school_scholarship_funding_source`` work
    instructions.
    """

    @classmethod
    def setUpClass(cls):
        """Create the records and configuration required by the tour."""
        super().setUpClass()
        # Pre-Condition for the create tour (docs/
        # school_scholarship_funding_source/01-create.md): an analytic
        # account, picked from the m2o dropdown by its unique name.
        cls.tour_analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "TOUR Funding Source Analytic",
            }
        )

        # Pre-Condition for Generate Code (docs/
        # school_scholarship_funding_source/01-create.md, Flow 6): an
        # active sequence.template for this model is required, or
        # clicking the button raises a UserError instead of assigning a
        # code.
        cls.code_sequence = cls.env["ir.sequence"].create(
            {
                "name": "TOUR Funding Source Code Sequence",
                "code": "ssi_school_scholarship.tour.school_scholarship_funding_source",
                "prefix": "TOURSEQFND",
                "padding": 4,
            }
        )
        cls.code_sequence_template = cls.env["sequence.template"].create(
            {
                "name": "TOUR Funding Source Sequence Template",
                "model_id": cls.env["ir.model"]._get_id(
                    "school_scholarship_funding_source"
                ),
                "sequence_field_id": cls.env["ir.model.fields"]
                ._get("school_scholarship_funding_source", "code")
                .id,
                "date_field_id": cls.env["ir.model.fields"]
                ._get("school_scholarship_funding_source", "create_date")
                .id,
                "sequence_selection_method": "use_sequence",
                "sequence_id": cls.code_sequence.id,
            }
        )

    def test_create(self):
        """Run the create tour for ``school_scholarship_funding_source``.

        IK: docs/school_scholarship_funding_source/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_school_scholarship_funding_source_create",
            login="admin",
        )
