# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolScholarshipDeductionRecognitionSecurity(YamlTransactionCase):
    """Scenario tests for the ``school_scholarship_deduction_recognition``
    model's own group ladder, ACL, and authorization separation from
    ``school_scholarship_deduction``.
    """

    def test_school_scholarship_deduction_recognition_security(self):
        """Run the recognition group ladder and access control scenarios."""
        self.run_yaml_scenario(
            "test_data_school_scholarship_deduction_recognition_security.yaml"
        )
