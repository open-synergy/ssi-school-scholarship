# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SchoolScholarshipDeductionLine(models.Model):
    """
    Extends School Scholarship Deduction - Line, propagating the
    parent Deduction document's own Operating Unit onto this line's
    own ``account.move.line`` (created by
    ``mixin.account_move_single_line``).
    """

    _name = "school_scholarship_deduction_line"
    _inherit = "school_scholarship_deduction_line"

    def _prepare_standard_ml(self):
        """Add the parent Deduction's Operating Unit to this line's ML.

        :return: dict of ``account.move.line`` values
        """
        res = super()._prepare_standard_ml()
        res["operating_unit_id"] = self.deduction_id.operating_unit_id.id
        return res
