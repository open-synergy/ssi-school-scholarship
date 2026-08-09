# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolScholarshipDeduction(YamlTransactionCase):
    """Scenario tests for ``school_scholarship_deduction``."""

    def test_school_scholarship_deduction(self):
        """Run the compute, workflow, reconcile, and negative path
        scenarios, then assert the Funding line's ``name_get``.

        The ``name_get`` return value is asserted directly in Python
        (P1: nilai balik method; L-01/L-02,
        odoo-development-unit-test references/python-escape-hatch.md)
        on the multi-source Funding lines the YAML scenario above
        already created, since ``action: call`` in the YAML DSL
        discards a method's return value.
        """
        self.run_yaml_scenario("test_data_school_scholarship_deduction.yaml")
        funding = self.env["school_scholarship_award_funding"].search(
            [
                ("funding_source_id.name", "=", "D1 Funding Source A"),
                ("percentage", "=", 60.0),
            ],
            limit=1,
        )
        self.assertEqual(
            funding.name_get(),
            [(funding.id, "D1 Funding Source A (60%)")],
        )

    def test_insert_form_element_view_element_disabled(self):
        """``_insert_form_element`` must skip the statusbar
        reconfiguration when ``_automatically_insert_view_element``
        is falsy.

        That attribute is a hardcoded ``True`` class constant on this
        model (mirroring the toggle ``mixin.transaction`` itself
        defaults to ``False``), so no business flow can ever reach
        the ``False`` branch on this concrete model -- exercised
        directly with ``mock.patch.object`` instead (P6: mock/patch;
        L-15, odoo-development-unit-test
        references/python-escape-hatch.md).
        """
        deduction = self.env["school_scholarship_deduction"]
        view_arch = "<form><header/></form>"
        with mock.patch.object(
            type(deduction), "_automatically_insert_view_element", False
        ):
            result = deduction._insert_form_element(view_arch)
        self.assertEqual(result, view_arch)
