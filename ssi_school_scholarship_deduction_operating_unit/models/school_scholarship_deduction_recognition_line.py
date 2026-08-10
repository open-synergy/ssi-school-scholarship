# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SchoolScholarshipDeductionRecognitionLine(models.Model):
    """
    Extends School Scholarship Deduction Recognition - Line,
    propagating the parent Recognition document's own Operating Unit
    onto both the debit and credit ``account.move.line`` this line
    creates (via ``mixin.account_move_double_line``).
    """

    _name = "school_scholarship_deduction_recognition_line"
    _inherit = "school_scholarship_deduction_recognition_line"

    def _prepare_standard_ml(self, direction):
        """Add the parent Recognition's Operating Unit to both lines.

        :param direction: ``"debit"`` or ``"credit"``
        :return: dict of ``account.move.line`` values
        """
        res = super()._prepare_standard_ml(direction)
        res["operating_unit_id"] = self.recognition_id.operating_unit_id.id
        return res
