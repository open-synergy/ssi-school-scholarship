# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolScholarshipAdmissionGuard(YamlTransactionCase):
    """Scenario-driven tests for the admission scholarship guards."""

    def test_school_scholarship_admission_guard(self):
        """Run the draft award, term deletion and admission cancel scenario.

        Covers an award sourced from a Draft admission that already has
        a student profile reaching Open with a Schedule, rejecting
        Compute Payment and deletion of a payment term that a Schedule
        line refers to, and rejecting cancellation of the admission
        while the award is active until the award is cancelled.
        """
        self.run_yaml_scenario("test_data_school_scholarship_admission_guard.yaml")
