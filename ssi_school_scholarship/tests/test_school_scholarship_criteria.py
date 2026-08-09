# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolScholarshipCriteria(YamlTransactionCase):
    """Scenario tests for ``school_scholarship_criteria``."""

    def test_school_scholarship_criteria(self):
        """Run the CRUD and constraint scenarios for the criterion."""
        self.run_yaml_scenario("test_data_school_scholarship_criteria.yaml")
