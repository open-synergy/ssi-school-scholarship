# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.ssi_decorator import ssi_decorator

GROUP_VIEWER = "ssi_school_scholarship.school_scholarship_award_viewer_group"


class SchoolEnrollment(models.Model):
    """
    Adds scholarship visibility to the enrollment record.
    Exposes the committed scholarship amount and the awards linked to
    this enrollment so billing staff can see the discount that
    applies to it. This is a commitment figure only: it never touches
    ``school_enrollment_payment_term`` or its detail lines, which
    stay the source of the actual billed/realized amounts -- keeping
    the two journals cleanly separated.
    """

    _name = "school_enrollment"
    _inherit = [
        "school_enrollment",
    ]

    scholarship_award_ids = fields.One2many(
        string="Scholarship Awards",
        comodel_name="school_scholarship_award",
        inverse_name="enrollment_id",
        help="Scholarship awards linked to this enrollment.",
    )
    amount_scholarship = fields.Monetary(
        string="Scholarship Amount",
        compute="_compute_amount_scholarship",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        groups="ssi_school_scholarship.school_scholarship_award_viewer_group",
        help=(
            "Total scholarship of this enrollment: Scholarship "
            "Deduction plus Scholarship Cash. Only the deduction part "
            "reduces the billing; Cash is paid to the student and "
            "does not reduce it. Restricted to the Scholarship Award "
            "Viewer group."
        ),
    )
    amount_scholarship_deducted = fields.Monetary(
        string="Scholarship Deducted",
        compute="_compute_amount_scholarship_deduction_group",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        groups=GROUP_VIEWER,
        help=(
            "Scholarship already deducted from the payment terms of "
            "this enrollment: the sum of Scholarship Deducted of its "
            "payment terms that are neither cancelled nor voided."
        ),
    )
    amount_scholarship_undeducted = fields.Monetary(
        string="Scholarship Not Yet Deducted",
        compute="_compute_amount_scholarship_deduction_group",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        groups=GROUP_VIEWER,
        help=(
            "Scholarship still waiting to be deducted from the "
            "payment terms of this enrollment: the sum of Scholarship "
            "Not Yet Deducted of its payment terms that are neither "
            "cancelled nor voided."
        ),
    )
    amount_scholarship_deduction = fields.Monetary(
        string="Scholarship Deduction",
        compute="_compute_amount_scholarship_deduction_group",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        groups=GROUP_VIEWER,
        help=(
            "Effective scholarship deduction: Scholarship Deducted "
            "plus Scholarship Not Yet Deducted. The part of a "
            "partially realized schedule line that was not deducted "
            "stays billable and is deliberately not counted."
        ),
    )
    amount_scholarship_cash = fields.Monetary(
        string="Scholarship Cash",
        compute="_compute_amount_scholarship_cash_group",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        groups=GROUP_VIEWER,
        help=(
            "Scholarship paid to the student in cash: the sum of "
            "Amount Planned of the Cash schedule lines that are "
            "Scheduled or Realized, of Open or Done awards. It does "
            "not reduce the billing."
        ),
    )
    amount_scholarship_disbursed = fields.Monetary(
        string="Scholarship Disbursed",
        compute="_compute_amount_scholarship_cash_group",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        groups=GROUP_VIEWER,
        help=(
            "Scholarship Cash already paid out: the sum of Amount "
            "Realized of the Realized Cash schedule lines."
        ),
    )
    amount_scholarship_undisbursed = fields.Monetary(
        string="Scholarship Not Yet Disbursed",
        compute="_compute_amount_scholarship_cash_group",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        groups=GROUP_VIEWER,
        help=(
            "Scholarship Cash still waiting to be paid out: the sum "
            "of Amount Planned of the Scheduled Cash schedule lines "
            "of Open or Done awards."
        ),
    )
    scholarship_award_count = fields.Integer(
        string="Scholarship Award Count",
        compute="_compute_scholarship_award_count",
        store=False,
        compute_sudo=True,
        help="Number of scholarship awards linked to this enrollment.",
    )

    def _get_scholarship_cash_schedules(self):
        """Return the Cash schedule lines of the live awards.

        :return: schedule lines of Cash benefits whose award is Open
            or Done
        """
        self.ensure_one()
        schedules = self.scholarship_award_ids.filtered(
            lambda award: award.state in ("open", "done")
        ).mapped("schedule_ids")
        return schedules.filtered(lambda line: line.benefit_id.benefit_type == "cash")

    def _get_scholarship_terms(self):
        """Return the payment terms that count for the scholarship.

        Same filter as the Total of the billing breakdown: terms
        that are neither cancelled nor voided.

        :return: payment terms to be summed
        """
        self.ensure_one()
        return self.payment_term_ids.filtered(
            lambda term: term.state not in ("cancelled", "voided")
        )

    @api.depends(
        "payment_term_ids.state",
        "payment_term_ids.scholarship_amount_deducted",
        "payment_term_ids.scholarship_amount_undeducted",
    )
    def _compute_amount_scholarship_deduction_group(self):
        """Sum the scholarship deduction of the counted payment terms.

        :return: nothing; assigns ``amount_scholarship_deducted``,
            ``amount_scholarship_undeducted`` and
            ``amount_scholarship_deduction``
        """
        for record in self:
            deducted = undeducted = 0.0
            for term in record._get_scholarship_terms():
                deducted += term.scholarship_amount_deducted
                undeducted += term.scholarship_amount_undeducted
            record.amount_scholarship_deducted = deducted
            record.amount_scholarship_undeducted = undeducted
            record.amount_scholarship_deduction = deducted + undeducted

    @api.depends(
        "scholarship_award_ids.state",
        "scholarship_award_ids.schedule_ids.state",
        "scholarship_award_ids.schedule_ids.amount_planned",
        "scholarship_award_ids.schedule_ids.amount_realized",
        "scholarship_award_ids.schedule_ids.benefit_id.benefit_type",
    )
    def _compute_amount_scholarship_cash_group(self):
        """Sum the Cash scholarship of the live awards.

        :return: nothing; assigns ``amount_scholarship_cash``,
            ``amount_scholarship_disbursed`` and
            ``amount_scholarship_undisbursed``
        """
        for record in self:
            cash = disbursed = undisbursed = 0.0
            for line in record._get_scholarship_cash_schedules():
                if line.state in ("scheduled", "realized"):
                    cash += line.amount_planned
                if line.state == "realized":
                    disbursed += line.amount_realized
                if line.state == "scheduled":
                    undisbursed += line.amount_planned
            record.amount_scholarship_cash = cash
            record.amount_scholarship_disbursed = disbursed
            record.amount_scholarship_undisbursed = undisbursed

    @api.depends(
        "amount_scholarship_deduction",
        "amount_scholarship_cash",
    )
    def _compute_amount_scholarship(self):
        """Sum the scholarship deduction and the scholarship cash.

        :return: nothing; assigns ``amount_scholarship``
        """
        for record in self:
            result = (
                record.amount_scholarship_deduction + record.amount_scholarship_cash
            )
            record.amount_scholarship = result

    def _get_amount_deduction(self):
        """Add the scholarship deduction to the billing deduction.

        Cash scholarship is not a deduction and is not added.

        :return: total effective deduction including the scholarship
        :rtype: float
        """
        result = super()._get_amount_deduction()
        for record in self.sudo():
            result += record.amount_scholarship_deduction
        return result

    def _get_amount_deducted(self):
        """Add the scholarship already deducted to the deducted part.

        :return: deduction already reconciled including the scholarship
        :rtype: float
        """
        result = super()._get_amount_deducted()
        for record in self.sudo():
            result += record.amount_scholarship_deducted
        return result

    @api.depends(
        "amount_scholarship_deduction",
        "amount_scholarship_deducted",
    )
    def _compute_amount_deduction(self):
        """Recompute the billing breakdown when the scholarship moves.

        The scholarship joins the breakdown through the hooks
        ``_get_amount_deduction`` and ``_get_amount_deducted``; this
        override only adds the dependencies.

        :return: nothing; see the base implementation
        """
        return super()._compute_amount_deduction()

    @api.depends("scholarship_award_ids")
    def _compute_scholarship_award_count(self):
        """Count the scholarship awards linked to this enrollment.

        :return: nothing; assigns ``scholarship_award_count``
        """
        for record in self:
            record.scholarship_award_count = len(record.scholarship_award_ids)

    def action_open_scholarship_award(self):
        """Open the list of scholarship awards linked to this enrollment.

        :return: an ``ir.actions.act_window`` dict
        """
        for record in self.sudo():
            result = record._open_scholarship_award()
        return result

    def _open_scholarship_award(self):
        """Build the window action listing this enrollment's awards.

        :return: an ``ir.actions.act_window`` dict limited to the
            scholarship awards of this enrollment
        """
        self.ensure_one()
        waction = self.env.ref(
            "ssi_school_scholarship.school_scholarship_award_action"
        ).read()[0]
        waction.update(
            {
                "domain": [("enrollment_id", "=", self.id)],
                "context": {"default_enrollment_id": self.id},
            }
        )
        return waction

    @ssi_decorator.pre_cancel_action()
    def _20_check_scholarship_award_active(self):
        """Reject cancelling an enrollment with an active award.

        A scholarship award is active while its state is neither
        ``cancel`` nor ``reject``.

        :raises UserError: when an active scholarship award is
            sourced from this enrollment.
        :return: None
        """
        self.ensure_one()
        award = (
            self.env["school_scholarship_award"]
            .sudo()
            .search(
                [
                    ("source_type", "=", "enrollment"),
                    ("enrollment_id", "=", self.id),
                    ("state", "not in", ["cancel", "reject"]),
                ],
                limit=1,
            )
        )
        if award:
            error_message = """
Document Type: %s
Context: Cancel enrollment
Database ID: %s
Problem: Enrollment has an active scholarship award '%s'
Solution: Cancel the scholarship award before cancelling this enrollment
""" % (
                self._description,
                self.id,
                award.display_name,
            )
            raise UserError(_(error_message))
