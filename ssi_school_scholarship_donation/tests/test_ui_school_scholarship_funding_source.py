# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiSchoolScholarshipFundingSource(HttpSavepointCase):
    """Tour test for the Donation Fund field on
    ``school_scholarship_funding_source`` create.
    """

    def test_create(self):
        """Run the create tour for ``school_scholarship_funding_source``.

        IK: docs/school_scholarship_funding_source/01-create.md (E1
        delta -- Additional Fields)
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_donation_"
            "school_scholarship_funding_source_create",
            login="admin",
        )
