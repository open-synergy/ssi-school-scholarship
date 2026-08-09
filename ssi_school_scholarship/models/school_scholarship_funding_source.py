# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolScholarshipFundingSource(models.Model):
    """
    Represents an envelope of scholarship budget (a pagu) tied to a single
    analytic account dimension.
    A funding source never holds money by itself — the donation module
    credits its analytic account when funds come in, and scholarship
    awards debit it when funds are used. This model only carries the
    dimension (analytic_account_id) and an optional manual ceiling; the
    actual balance, donor, and restriction information belong to the
    donation module and are intentionally out of scope here.
    """

    _name = "school_scholarship_funding_source"
    _inherit = ["mixin.master_data"]
    _description = "School Scholarship Funding Source"
    _order = "name, id"

    analytic_account_id = fields.Many2one(
        string="Analytic Account",
        comodel_name="account.analytic.account",
        required=True,
        ondelete="restrict",
        help="Analytic account this funding source is bound to. This is "
        "the sole boundary between the scholarship and donation "
        "modules: the donation module credits this analytic account "
        "when funds come in, and scholarship awards debit it when "
        "funds are used. Each analytic account may only be bound to "
        "one funding source.",
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.company,
        help="Company that owns this funding source.",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
        help="Currency the Ceiling amount is expressed in.",
    )
    school_id = fields.Many2one(
        string="School",
        comodel_name="school",
        help="School this funding source is earmarked for. Leave empty "
        "when the funding source is shared across every school.",
    )
    academic_year_id = fields.Many2one(
        string="Academic Year",
        comodel_name="school_academic_year",
        help="Academic year this funding source is earmarked for. Leave "
        "empty when the funding source is not tied to a single "
        "academic year.",
    )
    amount_ceiling = fields.Monetary(
        string="Ceiling",
        currency_field="currency_id",
        default=0.0,
        help="Maximum amount this funding source may disburse in total, "
        "entered manually. Zero means there is no ceiling.",
    )
    award_funding_ids = fields.One2many(
        string="Award Fundings",
        comodel_name="school_scholarship_award_funding",
        inverse_name="funding_source_id",
        help="Award funding lines drawing from this funding source.",
    )
    amount_committed = fields.Monetary(
        string="Amount Committed",
        currency_field="currency_id",
        compute="_compute_amount_committed",
        store=True,
        compute_sudo=True,
        help="Total amount committed against this funding source by "
        "awards whose Funding line references it and whose state is "
        "Open or Done.",
    )
    amount_realized = fields.Monetary(
        string="Amount Realized",
        currency_field="currency_id",
        compute="_compute_amount_realized",
        store=True,
        compute_sudo=True,
        help="Total amount already realized against this funding "
        "source. Always zero for now: the schedule model this is "
        "derived from is not part of this item's scope and is wired "
        "up in a later item.",
    )
    amount_available = fields.Monetary(
        string="Amount Available",
        currency_field="currency_id",
        compute="_compute_amount_available",
        store=True,
        compute_sudo=True,
        help="Remaining amount this funding source may still commit "
        "(Ceiling minus Amount Committed). Zero Ceiling means there "
        "is no ceiling, but is not treated as unlimited here.",
    )

    @api.depends(
        "award_funding_ids.amount_committed",
        "award_funding_ids.award_id.state",
    )
    def _compute_amount_committed(self):
        """Sum committed amounts of Open/Done awards on this source.

        :return: nothing; assigns ``amount_committed``
        """
        for record in self:
            lines = record.award_funding_ids.filtered(
                lambda line: line.award_id.state in ("open", "done")
            )
            record.amount_committed = sum(lines.mapped("amount_committed"))

    @api.depends()
    def _compute_amount_realized(self):
        """Return zero until the schedule model exists.

        No real dependency: the per-period schedule model this
        should be derived from is not part of this item's scope, so
        the value is a fixed placeholder wired up in a later item.

        :return: nothing; assigns ``amount_realized``
        """
        for record in self:
            record.amount_realized = 0.0

    @api.depends("amount_ceiling", "amount_committed")
    def _compute_amount_available(self):
        """Compute the still-uncommitted portion of the ceiling.

        :return: nothing; assigns ``amount_available``
        """
        for record in self:
            record.amount_available = (
                record.amount_ceiling - record.amount_committed
            )

    @api.constrains("analytic_account_id")
    def _check_analytic_account_id(self):
        """Forbid an Analytic Account already bound to another record.

        The analytic account is the only interface between the
        scholarship and donation modules, so a single analytic account
        must never be shared by two funding sources — otherwise a
        debit posted by one scholarship award could not be told apart
        from a debit posted by another funding source's award.

        :raises ValidationError: when another
            ``school_scholarship_funding_source`` record already uses
            the same ``analytic_account_id``.
        """
        # No falsy-value guard: ``analytic_account_id`` is ``required``,
        # and its DB column carries a NOT NULL constraint enforced by
        # the actual INSERT/UPDATE, which always runs before this
        # ``@api.constrains`` method (see ``BaseModel.create``/
        # ``write``). A record can therefore never reach this method
        # with an empty ``analytic_account_id``, so such a guard would
        # be dead code.
        for record in self:
            duplicate_count = self.search_count(
                [
                    ("id", "!=", record.id),
                    ("analytic_account_id", "=", record.analytic_account_id.id),
                ]
            )
            if duplicate_count > 0:
                error_message = """
Document Type: %s
Context: Configure analytic account
Database ID: %s
Problem: Analytic Account is already used by another Funding Source
Solution: Select an Analytic Account that is not yet bound to any
Funding Source
""" % (
                    self._description,
                    record.id,
                )
                raise ValidationError(_(error_message))
