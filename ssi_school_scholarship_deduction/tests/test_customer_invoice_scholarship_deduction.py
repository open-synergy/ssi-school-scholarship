# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCustomerInvoiceScholarshipDeduction(YamlTransactionCase):
    """Scenario tests for the ``customer_invoice`` scholarship split."""

    def test_customer_invoice_scholarship_deduction(self):
        """Run the scholarship/cash split compute and negative-path
        scenarios for ``customer_invoice``.
        """
        self.run_yaml_scenario(
            "test_data_customer_invoice_scholarship_deduction.yaml"
        )
