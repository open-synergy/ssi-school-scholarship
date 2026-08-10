# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolScholarshipDeductionOperatingUnit(YamlTransactionCase):
    """YAML-scenario tests for the Operating Unit adaptor of the School
    Scholarship Deduction module.
    """

    def test_school_scholarship_deduction_operating_unit(self):
        """Run every scenario in the module's own YAML fixture.

        :return: nothing
        """
        self.run_yaml_scenario(
            "test_data_school_scholarship_deduction_operating_unit.yaml"
        )
