# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase
from psycopg2 import IntegrityError

from odoo.tests import tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestSchoolScholarshipFundingSource(YamlTransactionCase):
    """Scenario tests for ``school_scholarship_funding_source``."""

    def test_school_scholarship_funding_source(self):
        """Run the CRUD and constraint scenarios for the funding source."""
        self.run_yaml_scenario("test_data_school_scholarship_funding_source.yaml")

    @mute_logger("odoo.sql_db")
    def test_analytic_account_id_is_required(self):
        """Reject a funding source without an Analytic Account.

        Pure Python — trigger P5 (L-22: the ``NOT NULL`` violation this
        required ``Many2one`` raises is a ``psycopg2.IntegrityError``,
        which is outside the 12 error types ``expect_error`` understands).
        ``mute_logger`` silences the PostgreSQL ERROR line this
        intentionally raises so ``oca_checklog_odoo`` does not fail CI.
        """
        with self.assertRaises(IntegrityError):
            self.env["school_scholarship_funding_source"].create(
                {
                    "name": "Missing Analytic Account",
                    "code": "TSCHF999",
                }
            )
