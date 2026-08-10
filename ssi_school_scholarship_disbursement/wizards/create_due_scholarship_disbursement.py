# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CreateDueScholarshipDisbursement(models.TransientModel):
    """
    Wizard that realizes every due Cash Schedule line of one or more
    Scholarship Awards -- selected from the Award's own form or from
    several Awards selected in the list view -- into draft
    ``school_scholarship_disbursement`` documents. Delegates the
    actual realization, Award by Award, to
    ``school_scholarship_award._create_due_disbursement``.
    """

    _name = "create_due_scholarship_disbursement"
    _description = "Create Due Scholarship Disbursement"

    award_ids = fields.Many2many(
        string="Awards",
        comodel_name="school_scholarship_award",
        relation="rel_create_due_scholarship_disbursement_award",
        column1="wizard_id",
        column2="award_id",
        readonly=True,
        help="Awards whose due Cash Schedule lines will be realized "
        "into Disbursement documents.",
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

    def action_create_due_disbursement(self):
        """Realize the selected Awards' due Cash Schedule lines.

        :return: an ``ir.actions.act_window`` dict listing the newly
            created ``school_scholarship_disbursement`` documents
        """
        for record in self.sudo():
            result = record._create_due_disbursement()
        return result

    def _create_due_disbursement(self):
        """Realize every selected Award's due Cash Schedule lines.

        Delegates to each Award's own ``_create_due_disbursement``,
        then opens the resulting documents. Raises when nothing at
        all was created across every selected Award, since that
        usually means none of the selected Awards has a due Cash
        Schedule line yet.

        :return: an ``ir.actions.act_window`` dict opening the newly
            created ``school_scholarship_disbursement`` documents
        :raises UserError: when no Disbursement document was created
            for any of the selected Awards
        """
        self.ensure_one()
        disbursements = self.env["school_scholarship_disbursement"]
        for award in self.award_ids:
            disbursements |= award._create_due_disbursement(
                self.date_start, self.date_end
            )
        self._check_disbursements(disbursements)
        return self._open_disbursements(disbursements)

    def _check_disbursements(self, disbursements):
        """Reject a run that created no Disbursement document at all.

        :param disbursements: the ``school_scholarship_disbursement``
            recordset created by this run
        :raises UserError: when ``disbursements`` is empty
        """
        self.ensure_one()
        if not disbursements:
            error_message = (
                _(
                    """
Context: Create due scholarship disbursement
Database ID: %s
Problem: No Disbursement document was created for the selected Award(s)
Solution: Check that a Cash Schedule line is due within the selected period
"""
                )
                % (self.id,)
            )
            raise UserError(error_message)

    def _open_disbursements(self, disbursements):
        """Build the window action listing the newly created documents.

        :param disbursements: the ``school_scholarship_disbursement``
            recordset just created
        :return: an ``ir.actions.act_window`` dict
        """
        self.ensure_one()
        waction = self.env.ref(
            "ssi_school_scholarship_disbursement."
            "school_scholarship_disbursement_action"
        ).read()[0]
        waction.update(
            {
                "view_mode": "tree,form",
                "domain": [("id", "in", disbursements.ids)],
            }
        )
        return waction
