# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CreateDueScholarshipDeduction(models.TransientModel):
    """
    Wizard that realizes every due Schedule line of one or more
    Scholarship Awards -- selected from the Award's own form or from
    several Awards selected in the list view -- into draft
    ``school_scholarship_deduction`` documents. Delegates the actual
    realization, Award by Award, to
    ``school_scholarship_award._create_due_deduction``.
    """

    _name = "create_due_scholarship_deduction"
    _description = "Create Due Scholarship Deduction"

    award_ids = fields.Many2many(
        string="Awards",
        comodel_name="school_scholarship_award",
        relation="rel_create_due_scholarship_deduction_award",
        column1="wizard_id",
        column2="award_id",
        readonly=True,
        help="Awards whose due Schedule lines will be realized into "
        "Deduction documents.",
    )
    date_start = fields.Date(
        string="Date Start",
        help="Earliest Schedule Date to process. Leave empty for no " "lower bound.",
    )
    date_end = fields.Date(
        string="Date End",
        required=True,
        help="Latest Schedule Date to process.",
    )

    @api.model
    def default_get(self, fields_list):
        """Prefill Awards from the form or list view selection.

        :param fields_list: field names requested by the client
        :return: dict of default values
        """
        res = super().default_get(fields_list)
        if self.env.context.get("active_model") == "school_scholarship_award":
            active_ids = self.env.context.get("active_ids", [])
            res["award_ids"] = [(6, 0, active_ids)]
        return res

    def action_create_due_deduction(self):
        """Realize the selected Awards' due Schedule lines.

        :return: an ``ir.actions.act_window`` dict listing the newly
            created ``school_scholarship_deduction`` documents
        """
        for record in self.sudo():
            result = record._create_due_deduction()
        return result

    def _create_due_deduction(self):
        """Realize every selected Award's due Schedule lines.

        Delegates to each Award's own ``_create_due_deduction``, then
        opens the resulting documents. Raises when nothing at all was
        created across every selected Award, since that usually means
        the target period has not been invoiced yet.

        :return: an ``ir.actions.act_window`` dict opening the newly
            created ``school_scholarship_deduction`` documents
        :raises UserError: when no Deduction document was created for
            any of the selected Awards
        """
        self.ensure_one()
        deductions = self.env["school_scholarship_deduction"]
        for award in self.award_ids:
            deductions |= award._create_due_deduction(self.date_start, self.date_end)
        self._check_deductions(deductions)
        return self._open_deductions(deductions)

    def _check_deductions(self, deductions):
        """Reject a run that created no Deduction document at all.

        :param deductions: the ``school_scholarship_deduction``
            recordset created by this run
        :raises UserError: when ``deductions`` is empty
        """
        self.ensure_one()
        if not deductions:
            error_message = (
                _(
                    """
Context: Create due scholarship deduction
Database ID: %s
Problem: No Deduction document was created for the selected Award(s)
Solution: Check that the period's invoice has already been issued
"""
                )
                % (self.id,)
            )
            raise UserError(error_message)

    def _open_deductions(self, deductions):
        """Build the window action listing the newly created documents.

        :param deductions: the ``school_scholarship_deduction``
            recordset just created
        :return: an ``ir.actions.act_window`` dict
        """
        self.ensure_one()
        waction = self.env.ref(
            "ssi_school_scholarship_deduction.school_scholarship_deduction_action"
        ).read()[0]
        waction.update(
            {
                "view_mode": "tree,form",
                "domain": [("id", "in", deductions.ids)],
            }
        )
        return waction
