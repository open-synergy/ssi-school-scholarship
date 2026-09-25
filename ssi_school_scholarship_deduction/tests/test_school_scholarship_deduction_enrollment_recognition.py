# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolScholarshipDeductionEnrollmentRecognition(YamlTransactionCase):
    """Scenario tests for the ``enrollment`` Recognition Method."""

    def test_school_scholarship_deduction_enrollment_recognition(self):
        """Run every enrollment-mode recognition scenario.

        Covers setting Recognition Method to ``enrollment`` on open,
        the resulting Revenue Recognition Line posted when the
        enrollment reaches Done, its exclusion from the due
        recognition wizard's own domain, rejecting cancellation once
        recognized, staying ``immediate`` when Revenue Recognition is
        disabled or the Award has no Deferred Discount Account,
        staying ``immediate`` for a deduction opened after the
        enrollment is already Done, and rejecting finishing the
        enrollment while one of its own deductions is not yet Open.
        """
        self.run_yaml_scenario(
            "test_data_school_scholarship_deduction_enrollment_recognition.yaml"
        )
