# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CreateDueScholarshipRecognition(models.TransientModel):
    """
    Wizard that releases every due, deferred scholarship deduction --
    ``recognition_state`` ``pending`` and ``recognition_date`` on or
    before the selected Date -- into one draft
    ``school_scholarship_deduction_recognition`` document each, for
    the deduction's own full ``amount_deferred``.
    """

    _name = "create_due_scholarship_recognition"
    _description = "Create Due Scholarship Recognition"

    date = fields.Date(
        string="Date",
        required=True,
        default=fields.Date.context_today,
        help="Recognition documents are created for every deduction "
        "whose own Recognition Date falls on or before this date, "
        "and this is also the Date of every document created.",
    )
    deduction_ids = fields.Many2many(
        string="Deductions",
        comodel_name="school_scholarship_deduction",
        relation="rel_create_due_scholarship_recognition_deduction",
        column1="wizard_id",
        column2="deduction_id",
        readonly=True,
        help="Deferred deductions due for recognition as of Date, "
        "computed automatically.",
    )

    @api.model
    def default_get(self, fields_list):
        """Prefill Deductions from today's due, deferred deductions.

        :param fields_list: field names requested by the client
        :return: dict of default values
        """
        res = super().default_get(fields_list)
        res["deduction_ids"] = [
            (6, 0, self._get_due_deduction_ids(fields.Date.today()))
        ]
        return res

    @api.onchange("date")
    def onchange_deduction_ids(self):
        """Refresh Deductions whenever Date changes.

        :return: nothing
        """
        self.deduction_ids = [(6, 0, self._get_due_deduction_ids(self.date))]

    def _get_due_deduction_ids(self, date):
        """Search deferred deductions due for recognition as of date.

        :param date: latest Recognition Date to include, or ``False``
            for no upper bound
        :return: list of matching ``school_scholarship_deduction`` ids
        """
        domain = [("recognition_state", "=", "pending")]
        if date:
            domain.append(("recognition_date", "<=", date))
        return self.env["school_scholarship_deduction"].search(domain).ids

    def action_create_due_recognition(self):
        """Release every selected Deduction's own Amount Deferred.

        :return: an ``ir.actions.act_window`` dict listing the newly
            created ``school_scholarship_deduction_recognition``
            documents
        """
        for record in self.sudo():
            result = record._create_due_recognition()
        return result

    def _create_due_recognition(self):
        """Create one draft Recognition per selected Deduction.

        :return: an ``ir.actions.act_window`` dict opening the newly
            created documents
        :raises UserError: when no Deduction is selected
        """
        self.ensure_one()
        self._check_deduction_ids()
        Recognition = self.env["school_scholarship_deduction_recognition"]
        recognitions = Recognition
        for deduction in self.deduction_ids:
            recognitions |= Recognition.create(
                self._prepare_due_recognition_data(deduction)
            )
        return self._open_recognitions(recognitions)

    def _check_deduction_ids(self):
        """Reject running the wizard with no Deduction selected.

        :raises UserError: when ``deduction_ids`` is empty
        """
        self.ensure_one()
        if not self.deduction_ids:
            error_message = (
                _(
                    """
Context: Create due scholarship recognition
Database ID: %s
Problem: No Deduction is due for recognition as of the selected Date
Solution: Pick a later Date, or check the deductions' own Recognition Date
"""
                )
                % (self.id,)
            )
            raise UserError(error_message)

    def _prepare_due_recognition_data(self, deduction):
        """Build one Recognition document's create values.

        :param deduction: the due, deferred
            ``school_scholarship_deduction`` being released
        :return: dict of
            ``school_scholarship_deduction_recognition`` values
        """
        self.ensure_one()
        return {
            "deduction_id": deduction.id,
            "date": self.date,
            "amount": deduction.amount_deferred,
            "journal_id": deduction.recognition_journal_id.id,
        }

    def _open_recognitions(self, recognitions):
        """Build the window action listing the newly created documents.

        :param recognitions: the
            ``school_scholarship_deduction_recognition`` recordset
            just created
        :return: an ``ir.actions.act_window`` dict
        """
        self.ensure_one()
        waction = self.env.ref(
            "ssi_school_scholarship_deduction."
            "school_scholarship_deduction_recognition_action"
        ).read()[0]
        waction.update(
            {
                "view_mode": "tree,form",
                "domain": [("id", "in", recognitions.ids)],
            }
        )
        return waction
