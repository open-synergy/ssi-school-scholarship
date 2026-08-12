# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestModuleCategory(YamlTransactionCase):
    """Scenario tests for the ``school_scholarship_award`` module
    categories, run against the security data declared in
    ``security/ir_module_category/`` and ``security/res_groups/``.
    """

    def test_module_category(self):
        """Run the award category/group repointing scenarios."""
        self.run_yaml_scenario("test_data_module_category.yaml")
