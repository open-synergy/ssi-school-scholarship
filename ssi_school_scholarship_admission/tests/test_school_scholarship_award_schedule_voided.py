# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolScholarshipAwardScheduleVoided(
    YamlTransactionCase
):  # pylint: disable=too-few-public-methods
    """Cover Base Amount recomputing on a ``voided`` detail line.

    Widens ``_compute_base_amount``'s ``@api.depends`` to
    ``payment_term_id.detail_ids.voided`` and
    ``admission_payment_term_id.detail_ids.voided`` so a Schedule
    line's Base Amount is recomputed the moment a detail on either
    term type is flagged ``voided`` -- without touching the Schedule
    line itself.
    """

    def test_school_scholarship_award_schedule_voided(self):
        """Run every Base Amount / voided detail scenario."""
        self.run_yaml_scenario(
            "test_data_school_scholarship_award_schedule_voided.yaml"
        )
