# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolAdmissionPaymentTerm(YamlTransactionCase):
    """Scenario tests for the scholarship figures glued onto
    ``school_admission_payment_term``.
    """

    def test_school_admission_payment_term_scholarship(self):
        """Run the payment term scholarship amounts scenario."""
        self.run_yaml_scenario("test_data_school_admission_payment_term.yaml")
