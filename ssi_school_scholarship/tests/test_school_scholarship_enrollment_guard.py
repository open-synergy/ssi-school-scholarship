# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolScholarshipEnrollmentGuard(YamlTransactionCase):
    """Scenario-driven tests for the enrollment scholarship guards."""

    def test_school_scholarship_enrollment_guard(self):
        """Run the payment term deletion and enrollment cancel scenario.

        Covers an award sourced from a Draft enrollment reaching Open
        with a Schedule, rejecting Compute Payment and deletion of a
        payment term that a Schedule line refers to, and rejecting
        cancellation of the enrollment while the award is active
        until the award is cancelled.
        """
        self.run_yaml_scenario("test_data_school_scholarship_enrollment_guard.yaml")
