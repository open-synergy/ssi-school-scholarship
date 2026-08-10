# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SchoolScholarshipDeductionRecognition(models.Model):
    """
    Extends School Scholarship Deduction Recognition with single
    operating unit support.

    Derives ``operating_unit_id`` from the parent Deduction
    document's own Operating Unit (create-time and onchange), and
    propagates it to the ``account.move`` this document creates on
    ``action_done`` (``_prepare_standard_move``). This document's own
    ``account.move.line`` records come from its Recognition Lines
    (``mixin.account_move_double_line``), not from this header
    directly -- see
    ``school_scholarship_deduction_recognition_line._prepare_standard_ml``.
    """

    _name = "school_scholarship_deduction_recognition"
    _inherit = [
        "school_scholarship_deduction_recognition",
        "mixin.single_operating_unit",
    ]

    @api.model
    def create(self, vals):
        """Derive ``operating_unit_id`` from the parent Deduction.

        Overridden so ``operating_unit_id`` always reflects the
        parent Deduction's own Operating Unit rather than the
        creating user's default operating unit from
        ``mixin.single_operating_unit``, unless the caller explicitly
        passes ``operating_unit_id`` in the same ``vals``.

        :param vals: values for the new record
        :return: the created
            ``school_scholarship_deduction_recognition`` record
        """
        self._derive_operating_unit_from_deduction(vals)
        return super().create(vals)

    def _derive_operating_unit_from_deduction(self, vals):
        """Mutate ``vals`` in place, deriving ``operating_unit_id``.

        Applies only when ``deduction_id`` is present in ``vals`` and
        the caller has not already supplied ``operating_unit_id``
        explicitly in the same ``vals`` -- an explicit value always
        wins.

        :param vals: the ``create`` values dict, mutated in place
        :return: None
        """
        if "deduction_id" not in vals or "operating_unit_id" in vals:
            return
        deduction = self.env["school_scholarship_deduction"].browse(
            vals["deduction_id"]
        )
        if deduction.operating_unit_id:
            vals["operating_unit_id"] = deduction.operating_unit_id.id

    @api.onchange("deduction_id")
    def onchange_operating_unit_id(self):
        """Set ``operating_unit_id`` from the parent Deduction.

        Mirrors the ``create`` derivation so the form shows the
        correct Operating Unit as soon as a Deduction is selected.

        :return: nothing
        """
        self.operating_unit_id = False
        if self.deduction_id:
            self.operating_unit_id = self.deduction_id.operating_unit_id

    def _prepare_standard_move(self):
        """Add this document's Operating Unit to the ``account.move``.

        :return: dict of ``account.move`` values
        """
        res = super()._prepare_standard_move()
        res["operating_unit_id"] = self.operating_unit_id.id
        return res
