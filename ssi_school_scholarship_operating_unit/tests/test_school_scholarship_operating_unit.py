# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolScholarshipOperatingUnit(
    YamlTransactionCase
):  # pylint: disable=too-few-public-methods
    """Cover the Operating Unit adaptor for the scholarship core models.

    Covers ``school_scholarship_award`` create/write/onchange
    derivation from the selected enrollment's school, storage of
    multiple Operating Units on the master data models
    (``school_scholarship_type``, ``school_scholarship_funding_source``,
    ``school_scholarship_program``), and the Operating Unit record
    rule denying access to an award outside a restricted user's own
    Operating Units.
    """

    def test_school_scholarship_operating_unit(self):
        """Run every scholarship Operating Unit adaptor scenario."""
        self.run_yaml_scenario("test_data_school_scholarship_operating_unit.yaml")
