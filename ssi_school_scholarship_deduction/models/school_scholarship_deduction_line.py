# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SchoolScholarshipDeductionLine(models.Model):
    """
    Represents one debit line of a scholarship deduction document.
    A line is generated per (Schedule line, Funding line) pairing: a
    schedule realized by two funding sources becomes two lines, each
    posting to the same ``final_account_id`` but carrying a different
    ``analytic_account_id``. ``price_unit`` (with ``uom_quantity``
    left at its mixin default of 1) is the Schedule line's Amount
    Planned multiplied by the Funding line's Percentage. This line's
    own ``account.move.line`` is created by ``_create_standard_ml``
    (``mixin.account_move_single_line``) as part of the header's
    ``_10_create_accounting_entry`` hook.
    """

    _name = "school_scholarship_deduction_line"
    _inherit = [
        "mixin.product_line_account",
        "mixin.account_move_single_line",
    ]
    _description = "School Scholarship Deduction - Line"
    _order = "deduction_id, sequence, id"

    # Accounting Move Single Line Mixin (``mixin.account_move_single_line``)
    _move_id_field_name = "move_id"
    _account_id_field_name = "account_id"
    _analytic_account_id_field_name = "analytic_account_id"
    _amount_currency_field_name = "price_subtotal"
    _date_field_name = "date"
    _normal_amount = "debit"

    deduction_id = fields.Many2one(
        string="# Deduction",
        comodel_name="school_scholarship_deduction",
        required=True,
        ondelete="cascade",
        help="Deduction document this line belongs to.",
    )
    schedule_id = fields.Many2one(
        string="Schedule",
        comodel_name="school_scholarship_award_schedule",
        required=True,
        ondelete="restrict",
        help="Award Schedule line this deduction line realizes.",
    )
    benefit_id = fields.Many2one(
        string="Benefit",
        comodel_name="school_scholarship_award_benefit",
        related="schedule_id.benefit_id",
        store=True,
        help="Benefit line of the selected Schedule line.",
    )
    funding_id = fields.Many2one(
        string="Funding",
        comodel_name="school_scholarship_award_funding",
        required=True,
        ondelete="restrict",
        help="Award Funding line this line's amount is drawn from.",
    )
    funding_source_id = fields.Many2one(
        string="Funding Source",
        comodel_name="school_scholarship_funding_source",
        related="funding_id.funding_source_id",
        store=True,
        help="Funding source of the selected Funding line.",
    )
    final_account_id = fields.Many2one(
        string="Final Account",
        comodel_name="account.account",
        required=True,
        ondelete="restrict",
        help="Final accounting destination of this line, copied from "
        "the Benefit line's own Account. In this item, ``account_id`` "
        "always equals this field; a later, deferred-recognition item "
        "may point ``account_id`` at a different, temporary account "
        "instead while keeping this field as the eventual target.",
    )
    account_id = fields.Many2one(
        compute="_compute_account_id",
        store=True,
        compute_sudo=True,
        # See the identical override, and the reason for
        # ``required=False``, on ``school_scholarship_award_benefit``:
        # a stored computed field's value is never included in the
        # initial ``INSERT``, so keeping the inherited NOT NULL
        # constraint makes every ``create()`` fail before this
        # compute ever runs.
        required=False,
        help="Accounting account this line posts to. Always equal to "
        "Final Account in this item.",
    )
    move_line_id = fields.Many2one(
        string="Journal Item",
        comodel_name="account.move.line",
        readonly=True,
        help="Journal item created for this line once the parent "
        "document is opened.",
    )

    # Convenience fields mirrored from the header, following the
    # pattern of ``customer_invoice.line``.
    move_id = fields.Many2one(
        related="deduction_id.move_id",
        compute_sudo=True,
    )
    date = fields.Date(
        related="deduction_id.date",
        compute_sudo=True,
    )
    currency_id = fields.Many2one(
        related="deduction_id.currency_id",
        compute_sudo=True,
        # ``mixin.product_line_price`` declares this field
        # ``required=True`` with its own stored default -- Odoo's field
        # inheritance merges attributes across `_inherit`, so redefining
        # the field here as a *non-stored* related field (no
        # ``store=True``) without clearing ``required`` leaves it
        # required=True with nothing to satisfy that requirement client
        # side until the row is actually saved. The same reasoning, and
        # the identical fix, already applies to ``account_id`` above and
        # to the sibling override on ``school_scholarship_award_benefit``.
        required=False,
    )
    company_id = fields.Many2one(
        related="deduction_id.company_id",
        compute_sudo=True,
    )
    company_currency_id = fields.Many2one(
        related="deduction_id.company_currency_id",
        compute_sudo=True,
    )
    analytic_account_id = fields.Many2one(
        related="funding_id.analytic_account_id",
        store=True,
        compute_sudo=True,
    )

    @api.depends("final_account_id")
    def _compute_account_id(self):
        """Copy Final Account into the posting account.

        :return: nothing; assigns ``account_id``
        """
        for record in self:
            record.account_id = record.final_account_id

    @api.onchange("schedule_id")
    def onchange_name(self):
        """Default the Description from the Schedule line's Benefit."""
        self.name = False
        if self.schedule_id:
            self.name = self.schedule_id.benefit_id.name

    @api.onchange("schedule_id")
    def onchange_product_id(self):
        """Default the Product from the Schedule line's Benefit."""
        self.product_id = False
        if self.schedule_id:
            self.product_id = self.schedule_id.benefit_id.product_id

    @api.onchange("schedule_id")
    def onchange_final_account_id(self):
        """Default Final Account from the Schedule line's Benefit."""
        self.final_account_id = False
        if self.schedule_id:
            self.final_account_id = self.schedule_id.benefit_id.account_id

    @api.onchange("schedule_id", "funding_id")
    def onchange_price_unit(self):
        """Default Price Unit from the Schedule and Funding percentage."""
        self.price_unit = 0.0
        if self.schedule_id and self.funding_id:
            self.price_unit = (
                self.schedule_id.amount_planned * self.funding_id.percentage / 100.0
            )

    def _get_standard_label(self):
        """Build the journal item label without the student's identity.

        Combines the parent document's own number with this line's
        Description (a cost component name, e.g. a Benefit/Product
        description) -- never the student's name, so the ledger stays
        silent about who is receiving the scholarship (see the
        Keputusan Desain confidentiality note).

        :return: the composed label string
        """
        self.ensure_one()
        return "%s - %s" % (self.deduction_id.name, self.name)
