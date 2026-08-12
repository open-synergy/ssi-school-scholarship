# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCreateDueScholarshipRecognition(YamlTransactionCase):
    """Onchange coverage for ``create_due_scholarship_recognition``.

    The wizard's own workflow (releasing a due deduction, and the
    empty-selection guard) is already covered in pure Python by
    ``test_school_scholarship_deduction_recognition.py`` (P1: the
    method under test returns an ``ir.actions.act_window`` dict /
    raises directly, discarded by ``action: call`` in the YAML DSL --
    odoo-development-unit-test references/python-escape-hatch.md).
    This file adds the ``action: form`` scenario that method cannot:
    ``onchange_deduction_ids`` only fires through the Form API.
    """

    def test_create_due_scholarship_recognition_onchange(self):
        """Run the wizard's ``onchange_deduction_ids`` scenario."""
        self.run_yaml_scenario("test_data_create_due_scholarship_recognition.yaml")
