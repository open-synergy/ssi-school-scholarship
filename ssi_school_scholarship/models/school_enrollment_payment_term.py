# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SchoolEnrollmentPaymentTerm(models.Model):
    # Extension of the enrollment payment term: refuses deleting a
    # term that a scholarship award Schedule line refers to, and
    # shows the scholarship deduction schedule of the term.
    _name = "school_enrollment_payment_term"
    _inherit = [
        "school_enrollment_payment_term",
    ]

    scholarship_schedule_ids = fields.One2many(
        string="Scholarship Schedules",
        comodel_name="school_scholarship_award_schedule",
        inverse_name="payment_term_id",
        readonly=True,
        help="Scholarship award schedule lines pinned to this payment "
        "term. Every scholarship on a payment term is a deduction "
        "(Fee Reduction); Cash benefits never refer to a payment "
        "term.",
    )
    scholarship_amount = fields.Monetary(
        string="Scholarship Amount",
        currency_field="currency_id",
        compute="_compute_scholarship_amount",
        store=True,
        compute_sudo=True,
        help="Scholarship committed to this payment term: the sum of "
        "Amount Planned of its Scheduled and Realized schedule lines "
        "whose award is Open or Done.",
    )
    scholarship_amount_deducted = fields.Monetary(
        string="Scholarship Deducted",
        currency_field="currency_id",
        compute="_compute_scholarship_amount_deducted",
        store=True,
        compute_sudo=True,
        help="Scholarship actually deducted from this payment term: "
        "the sum of Amount Realized of its Realized schedule lines.",
    )
    scholarship_amount_deducted_planned = fields.Monetary(
        string="Scholarship Deducted (Planned)",
        currency_field="currency_id",
        compute="_compute_scholarship_amount_deducted_planned",
        store=True,
        compute_sudo=True,
        help="Planned amount of the schedule lines that are already "
        "Realized: the sum of their Amount Planned. Compare with "
        "Scholarship Deducted to see the difference between plan "
        "and actual deduction.",
    )
    scholarship_amount_undeducted = fields.Monetary(
        string="Scholarship Not Yet Deducted",
        currency_field="currency_id",
        compute="_compute_scholarship_amount_undeducted",
        store=True,
        compute_sudo=True,
        help="Scholarship still waiting to be deducted from this "
        "payment term: the sum of Amount Planned of its Scheduled "
        "schedule lines whose award is Open or Done.",
    )

    @api.depends(
        "scholarship_schedule_ids.state",
        "scholarship_schedule_ids.amount_planned",
        "scholarship_schedule_ids.award_id.state",
    )
    def _compute_scholarship_amount(self):
        """Sum the committed scholarship of this payment term.

        Counts Scheduled and Realized schedule lines whose award is
        Open or Done; Skipped, Cancelled and Draft lines, and lines
        of a Draft award, are not a live commitment.

        :return: nothing; assigns ``scholarship_amount``
        """
        for record in self:
            lines = record.scholarship_schedule_ids.filtered(
                lambda line: line.state in ("scheduled", "realized")
                and line.award_id.state in ("open", "done")
            )
            result = sum(lines.mapped("amount_planned"))
            record.scholarship_amount = result

    @api.depends(
        "scholarship_schedule_ids.state",
        "scholarship_schedule_ids.amount_realized",
    )
    def _compute_scholarship_amount_deducted(self):
        """Sum the actual deduction of this payment term.

        :return: nothing; assigns ``scholarship_amount_deducted``
        """
        for record in self:
            lines = record.scholarship_schedule_ids.filtered(
                lambda line: line.state == "realized"
            )
            result = sum(lines.mapped("amount_realized"))
            record.scholarship_amount_deducted = result

    @api.depends(
        "scholarship_schedule_ids.state",
        "scholarship_schedule_ids.amount_planned",
    )
    def _compute_scholarship_amount_deducted_planned(self):
        """Sum the planned amount of the Realized schedule lines.

        :return: nothing; assigns
            ``scholarship_amount_deducted_planned``
        """
        for record in self:
            lines = record.scholarship_schedule_ids.filtered(
                lambda line: line.state == "realized"
            )
            result = sum(lines.mapped("amount_planned"))
            record.scholarship_amount_deducted_planned = result

    @api.depends(
        "scholarship_schedule_ids.state",
        "scholarship_schedule_ids.amount_planned",
        "scholarship_schedule_ids.award_id.state",
    )
    def _compute_scholarship_amount_undeducted(self):
        """Sum the scholarship not yet deducted from this term.

        Counts Scheduled schedule lines whose award is Open or
        Done.

        :return: nothing; assigns ``scholarship_amount_undeducted``
        """
        for record in self:
            lines = record.scholarship_schedule_ids.filtered(
                lambda line: line.state == "scheduled"
                and line.award_id.state in ("open", "done")
            )
            result = sum(lines.mapped("amount_planned"))
            record.scholarship_amount_undeducted = result

    def _check_scholarship_award_reference(self):
        """Reject deleting a payment term referred to by an award.

        Looks for a scholarship award Schedule line pinned to one of
        these terms. The state of the award does not matter: the
        database foreign key is ``restrict`` regardless of state.

        :raises UserError: naming the first referring award and the
            payment term it refers to.
        :return: None
        """
        if not self.ids:
            return
        schedule = (
            self.env["school_scholarship_award_schedule"]
            .sudo()
            .search(
                [("payment_term_id", "in", self.ids)],
                limit=1,
            )
        )
        if schedule:
            term = schedule.payment_term_id
            error_message = """
Document Type: %s
Context: Delete enrollment payment term
Database ID: %s
Problem: Payment term '%s' is referenced by scholarship award '%s'
Solution: Cancel the scholarship award before deleting its payment terms
""" % (
                self._description,
                term.id,
                term.display_name,
                schedule.award_id.display_name,
            )
            raise UserError(_(error_message))

    def unlink(self):
        """Refuse deleting payment terms referred to by an award.

        Guarding ``unlink`` (rather than the Compute Payment button)
        covers Compute Payment, the Copy Payment Term wizard, and
        manual deletion of a row in a single place.

        :raises UserError: when an award Schedule line refers to a
            deleted term.
        :return: ``True``
        """
        self._check_scholarship_award_reference()
        return super().unlink()
