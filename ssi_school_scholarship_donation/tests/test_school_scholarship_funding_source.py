# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.exceptions import ValidationError
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolScholarshipFundingSource(
    YamlTransactionCase
):  # pylint: disable=too-few-public-methods
    """Cover the ``mixin.donation_fund_consumer`` wiring on Funding Source.

    Covers binding/clearing/deleting a Funding Source's Donation Fund
    (ledger row creation, refresh through the award workflow, and
    removal), plus the Analytic Account mismatch negative path.
    """

    def test_school_scholarship_funding_source(self):
        """Run every Funding Source Donation Fund wiring scenario."""
        self.run_yaml_scenario("test_data_school_scholarship_funding_source.yaml")

    def test_donation_fund_analytic_mismatch_leaves_no_usage_row(self):
        """A mismatched Analytic Account raises, with no ledger row.

        Pure Python -- trigger P13 (L-26: YAML's ``expect_error`` runs
        the write inside a savepoint that is rolled back once the
        expected ``ValidationError`` is caught, so this negative
        path's *other* requirement -- that no ``donation_fund_usage``
        row was left behind by the rejected write -- could never be
        asserted from YAML). Calling ``write()`` directly here, with
        no savepoint around it, keeps the database state visible for
        assertion after the exception.
        """
        analytic_a = self.env["account.analytic.account"].create(
            {"name": "P13 Analytic A"}
        )
        analytic_b = self.env["account.analytic.account"].create(
            {"name": "P13 Analytic B"}
        )
        funding_source = self.env["school_scholarship_funding_source"].create(
            {
                "name": "P13 Funding Source",
                "code": "/",
                "analytic_account_id": analytic_a.id,
            }
        )
        fund = self.env["donation_fund"].create(
            {
                "name": "P13 Fund",
                "code": "/",
                "analytic_account_id": analytic_b.id,
            }
        )

        with self.assertRaises(ValidationError):
            funding_source.write({"donation_fund_id": fund.id})

        model = self.env["ir.model"].search(
            [("model", "=", "school_scholarship_funding_source")], limit=1
        )
        usage = self.env["donation_fund_usage"].search(
            [
                ("model_id", "=", model.id),
                ("res_id", "=", funding_source.id),
            ]
        )
        self.assertFalse(usage)
