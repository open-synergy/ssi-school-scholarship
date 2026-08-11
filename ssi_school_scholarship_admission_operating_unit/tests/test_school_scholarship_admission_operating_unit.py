# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolScholarshipAdmissionOperatingUnit(
    YamlTransactionCase
):  # pylint: disable=too-few-public-methods
    """Cover Operating Unit derivation for Admission-sourced awards.

    Covers ``school_scholarship_award`` creation with Billing Source
    Admission deriving ``operating_unit_id`` from the Admission's
    School (exactly one operating unit), re-derivation on ``write``
    when ``admission_id`` changes, an explicit ``operating_unit_id``
    never being overridden, the Enrollment-sourced path regression,
    and the negative path where the Admission's School has zero or
    more than one operating unit.
    """

    def test_school_scholarship_admission_operating_unit(self):
        """Run every Admission Operating Unit derivation scenario."""
        self.run_yaml_scenario(
            "test_data_school_scholarship_admission_operating_unit.yaml"
        )
