# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolScholarshipAward(YamlTransactionCase):
    """Scenario tests for ``school_scholarship_award``."""

    def test_school_scholarship_award(self):
        """Run the CRUD, workflow, onchange, and negative path scenarios."""
        self.run_yaml_scenario("test_data_school_scholarship_award.yaml")

    def test_insert_form_element_view_element_disabled(self):
        """``_insert_form_element`` must skip the statusbar
        reconfiguration when ``_automatically_insert_view_element``
        is falsy.

        That attribute is a hardcoded ``True`` class constant on this
        model (mirroring the toggle ``mixin.transaction`` itself
        defaults to ``False``), so no business flow can ever reach
        the ``False`` branch on this concrete model -- exercised
        directly with ``mock.patch.object`` instead (P: mock,
        odoo-development-unit-test references/python-escape-hatch.md).
        """
        award = self.env["school_scholarship_award"]
        view_arch = "<form><header/></form>"
        with mock.patch.object(
            type(award), "_automatically_insert_view_element", False
        ):
            result = award._insert_form_element(view_arch)
        self.assertEqual(result, view_arch)
