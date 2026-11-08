# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCustomerInvoiceForceDeleteScholarship(YamlTransactionCase):
    """Scenario tests for the force delete guard on ``customer_invoice``."""

    def test_customer_invoice_force_delete_scholarship(self):
        """Run the force delete guard negative and positive scenarios.

        An invoice referenced by a scholarship deduction allocation
        is rejected; an unreferenced one is not.
        """
        self.run_yaml_scenario(
            "test_data_customer_invoice_force_delete_scholarship.yaml"
        )
