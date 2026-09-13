# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolScholarshipDisbursementCancelPaid(YamlTransactionCase):
    """Scenario tests for cancelling a paid ``school_scholarship_disbursement``."""

    def test_school_scholarship_disbursement_cancel_paid(self):
        """Run the pre-cancel payment guard scenario.

        :return: nothing
        """
        self.run_yaml_scenario(
            "test_data_school_scholarship_disbursement_cancel_paid.yaml"
        )
