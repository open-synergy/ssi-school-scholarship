# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare


class SchoolScholarshipAwardFunding(models.Model):
    """
    Represents one funding line of a scholarship award.
    A funding line states what percentage of the award's
    ``amount_awarded`` is drawn from a given
    ``school_scholarship_funding_source``. The Percentage of every
    funding line of the same award must add up to exactly 100%, and a
    Funding Source may only appear once per award — both enforced
    here rather than by ``_sql_constraints``, so the affected lines
    can be identified in the error message.
    """

    _name = "school_scholarship_award_funding"
    _description = "School Scholarship Award Funding"
    _order = "sequence, id"

    award_id = fields.Many2one(
        string="Award",
        comodel_name="school_scholarship_award",
        required=True,
        ondelete="cascade",
        help="Scholarship award this funding line belongs to.",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=5,
        help="Display order of this funding line within the award.",
    )
    allowed_funding_source_ids = fields.Many2many(
        string="Allowed Funding Sources",
        comodel_name="school_scholarship_funding_source",
        compute="_compute_allowed_funding_source_ids",
        compute_sudo=True,
        help="Funding sources allowed by the award's Program, used to "
        "restrict the selectable Funding Source on this line.",
    )
    funding_source_id = fields.Many2one(
        string="Funding Source",
        comodel_name="school_scholarship_funding_source",
        required=True,
        ondelete="restrict",
        help="Funding source this line draws from. Restricted to the "
        "funding sources allowed by the award's Program.",
    )
    percentage = fields.Float(
        string="Percentage",
        digits=(5, 2),
        required=True,
        help="Percentage of the award's Amount Awarded drawn from "
        "this Funding Source. The Percentage of every funding line "
        "of the same award must add up to exactly 100%.",
    )
    amount_committed = fields.Monetary(
        string="Amount Committed",
        currency_field="currency_id",
        compute="_compute_amount_committed",
        store=True,
        compute_sudo=True,
        help="Portion of the award's Amount Awarded committed to this "
        "Funding Source (Percentage applied to the award's Amount "
        "Awarded).",
    )
    amount_realized = fields.Monetary(
        string="Amount Realized",
        currency_field="currency_id",
        compute="_compute_amount_realized",
        store=True,
        compute_sudo=True,
        help="Portion of the award's Amount Realized attributed to "
        "this Funding Source. Always zero for now: the schedule "
        "model this is derived from is not part of this item's "
        "scope and is wired up in a later item.",
    )
    analytic_account_id = fields.Many2one(
        string="Analytic Account",
        comodel_name="account.analytic.account",
        related="funding_source_id.analytic_account_id",
        store=True,
        help="Analytic account of the selected Funding Source.",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="award_id.company_currency_id",
        store=True,
        help="Currency the Amount Committed and Amount Realized "
        "fields are expressed in, following the award's Company "
        "Currency.",
    )

    @api.depends("award_id.program_id.funding_source_ids")
    def _compute_allowed_funding_source_ids(self):
        """Restrict selectable sources to the award's Program's.

        :return: nothing; assigns ``allowed_funding_source_ids``
        """
        for record in self:
            record.allowed_funding_source_ids = (
                record.award_id.program_id.funding_source_ids
            )

    @api.depends("percentage", "award_id.amount_awarded")
    def _compute_amount_committed(self):
        """Apply this line's percentage to the award's Amount Awarded.

        :return: nothing; assigns ``amount_committed``
        """
        for record in self:
            record.amount_committed = (
                record.award_id.amount_awarded * record.percentage / 100.0
            )

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

    @api.constrains("percentage", "award_id")
    def _check_percentage_total(self):
        """Require the award's funding percentages to add up to 100.

        Compared with ``float_compare`` at the award's company
        currency precision, since ``percentage`` is a plain
        ``Float`` with no currency of its own.

        :raises ValidationError: when the sum of ``percentage`` across
            every funding line of the same award is not exactly 100.
        """
        checked_awards = self.env["school_scholarship_award"]
        for record in self:
            award = record.award_id
            if not award or award in checked_awards:
                continue
            checked_awards |= award
            total_percentage = sum(award.funding_ids.mapped("percentage"))
            precision = award.company_currency_id.decimal_places
            if float_compare(total_percentage, 100.0, precision_digits=precision) != 0:
                error_message = """
Document Type: %s
Context: Configure award funding
Database ID: %s
Problem: Funding Percentage adds up to %s instead of 100
Solution: Adjust the Percentage of the funding lines so they add up to 100
""" % (
                    self._description,
                    award.id,
                    total_percentage,
                )
                raise ValidationError(_(error_message))

    @api.constrains("funding_source_id", "award_id")
    def _check_duplicate_funding_source(self):
        """Forbid two funding lines of the same award sharing a source.

        :raises ValidationError: when another funding line of the
            same award already uses the same ``funding_source_id``.
        """
        for record in self:
            if not record.funding_source_id:
                continue
            duplicate_count = self.search_count(
                [
                    ("id", "!=", record.id),
                    ("award_id", "=", record.award_id.id),
                    ("funding_source_id", "=", record.funding_source_id.id),
                ]
            )
            if duplicate_count > 0:
                error_message = """
Document Type: %s
Context: Configure award funding
Database ID: %s
Problem: Funding Source '%s' is already used by another funding line of this award
Solution: Select a Funding Source not yet used by this award, or remove the duplicate line
""" % (
                    self._description,
                    record.id,
                    record.funding_source_id.display_name,
                )
                raise ValidationError(_(error_message))
