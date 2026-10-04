# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolScholarshipDeductionInvoiceOrigin(YamlTransactionCase):
    """Scenario tests for the Open invoice-origin check."""

    def test_school_scholarship_deduction_invoice_origin(self):
        """Run the invoice-origin scenarios.

        Covers both rejections (allocation to another term's invoice,
        schedule without a customer invoice) and both acceptances (two
        deductions sharing one origin invoice, re-deduction after a
        cancel).
        """
        self.run_yaml_scenario(
            "test_data_school_scholarship_deduction_invoice_origin.yaml"
        )
