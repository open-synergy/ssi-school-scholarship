# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolScholarshipAwardPolicy(YamlTransactionCase):
    """Scenario tests for the ``create_disbursement_ok`` policy field."""

    def test_school_scholarship_award_policy(self):
        """Run the ``create_disbursement_ok`` policy scenarios."""
        self.run_yaml_scenario("test_data_school_scholarship_award_policy.yaml")
