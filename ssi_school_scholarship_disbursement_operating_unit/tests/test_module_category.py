# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestModuleCategory(YamlTransactionCase):
    """Scenario test asserting the disbursement Operating Unit group is
    repointed to the disbursement-specific data ownership category.
    """

    def test_module_category(self):
        """Run the disbursement Operating Unit group repointing
        scenario.
        """
        self.run_yaml_scenario("test_data_module_category.yaml")
