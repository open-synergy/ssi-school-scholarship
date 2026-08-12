# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestModuleCategory(YamlTransactionCase):
    """Scenario tests asserting the deduction Operating Unit group is
    repointed to the deduction-specific data ownership category, while
    the out-of-scope Deduction Recognition Operating Unit group is left
    untouched on the old shared category.
    """

    def test_module_category(self):
        """Run the deduction Operating Unit group repointing scenarios."""
        self.run_yaml_scenario("test_data_module_category.yaml")
