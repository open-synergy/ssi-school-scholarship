# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class CustomerInvoice(models.Model):
    """
    Splits how much of a customer invoice's Realized Amount was
    settled by a scholarship deduction versus an actual cash
    deposit.

    ``amount_realized`` alone cannot tell the two apart: a
    scholarship deduction reconciles the same receivable journal
    item a bank deposit would, so an invoice fully covered by a
    scholarship reports itself as fully Realized -- and eventually
    Paid -- without a single unit of cash ever moving. Cash receipt
    reports built directly on ``amount_realized`` would then
    overstate actual deposits. The distinction is read from the
    journal of the reconciled credit's own move: a scholarship
    journal is recognized by cross-checking it against the
    ``journal_id`` actually used by ``school_scholarship_deduction``
    documents, never by a hard-coded journal name.
    """

    _name = "customer_invoice"
    _inherit = [
        "customer_invoice",
    ]

    scholarship_deduction_ids = fields.Many2many(
        string="Scholarship Deductions",
        comodel_name="school_scholarship_deduction",
        compute="_compute_scholarship_deduction_ids",
        store=False,
        compute_sudo=True,
        help=(
            "Scholarship deduction documents that allocate part of "
            "their own Amount Total to this invoice, traced through "
            "their own Allocation lines. Not stored -- always "
            "reflects the current set of allocations."
        ),
    )
    amount_settled_by_scholarship = fields.Monetary(
        string="Settled by Scholarship",
        compute="_compute_amount_settled",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help=(
            "Portion of Realized Amount settled by scholarship "
            "deductions rather than an actual cash deposit. Excluded "
            "from Settled by Cash and from cash receipt reports."
        ),
    )
    amount_settled_by_cash = fields.Monetary(
        string="Settled by Cash",
        compute="_compute_amount_settled",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help=(
            "Realized Amount net of the portion settled by "
            "scholarship. Cash receipt reports must use this field "
            "instead of Realized Amount, or they overstate actual "
            "deposits on invoices partly or fully covered by a "
            "scholarship."
        ),
    )
    has_scholarship = fields.Boolean(
        string="Has Scholarship",
        compute="_compute_amount_settled",
        store=True,
        compute_sudo=True,
        help=(
            "True once at least part of this invoice has been "
            "settled by a scholarship deduction."
        ),
    )

    @api.depends(
        "receivable_move_line_id.matched_credit_ids",
        "receivable_move_line_id.matched_credit_ids.amount",
        "receivable_move_line_id.matched_credit_ids.credit_move_id.move_id.journal_id",
        "amount_realized",
    )
    def _compute_amount_settled(self):
        """Split Realized Amount into scholarship- and cash-settled.

        Walks the receivable journal item's matched credits (the
        ``account.partial.reconcile`` records where it is the debit
        side) and sums the ``amount`` of every pair whose credit
        move's own journal is used by at least one
        ``school_scholarship_deduction`` document -- so the
        scholarship journal is discovered from the deduction
        documents that actually exist, never hard-coded by name.

        :return: nothing; assigns ``amount_settled_by_scholarship``,
            ``amount_settled_by_cash``, and ``has_scholarship``
        """
        Deduction = self.env[  # pylint: disable=invalid-name
            "school_scholarship_deduction"
        ]
        for record in self:
            amount_settled_by_scholarship = 0.0
            partials = record.receivable_move_line_id.matched_credit_ids
            if partials:
                journal_ids = partials.mapped("credit_move_id.move_id.journal_id").ids
                scholarship_journal_ids = (
                    Deduction.sudo()
                    .search(
                        record._get_scholarship_deduction_journal_criteria(journal_ids)
                    )
                    .mapped("journal_id")
                    .ids
                )
                for partial in partials:
                    journal = partial.credit_move_id.move_id.journal_id
                    if journal.id in scholarship_journal_ids:
                        amount_settled_by_scholarship += partial.amount
            record.amount_settled_by_scholarship = amount_settled_by_scholarship
            record.amount_settled_by_cash = (
                record.amount_realized - amount_settled_by_scholarship
            )
            record.has_scholarship = amount_settled_by_scholarship > 0.0

    def _get_scholarship_deduction_journal_criteria(self, journal_ids):
        """Build the domain identifying scholarship journals.

        Extension point: override to change how a journal is
        recognized as belonging to a scholarship deduction.

        :param journal_ids: candidate ``account.journal`` ids, taken
            from the receivable line's matched credits
        :return: an Odoo search domain
        """
        self.ensure_one()
        return [("journal_id", "in", journal_ids)]

    def _compute_scholarship_deduction_ids(self):
        """Trace the scholarship deductions allocated to this invoice.

        No ``@api.depends``: the result is driven entirely by
        ``school_scholarship_deduction_allocation`` records that
        point at this invoice -- a relation with no field on this
        model itself to declare as a dependency. ``store=False``
        keeps the value fresh on every read instead.

        :return: nothing; assigns ``scholarship_deduction_ids``
        """
        Allocation = self.env[  # pylint: disable=invalid-name
            "school_scholarship_deduction_allocation"
        ]
        for record in self:
            allocations = Allocation.sudo().search(
                record._get_scholarship_deduction_allocation_criteria()
            )
            record.scholarship_deduction_ids = allocations.mapped("deduction_id").ids

    def _get_scholarship_deduction_allocation_criteria(self):
        """Build the domain selecting this invoice's own allocations.

        Extension point: override to broaden or narrow which
        allocation lines count toward ``scholarship_deduction_ids``.

        :return: an Odoo search domain
        """
        self.ensure_one()
        return [("customer_invoice_id", "=", self.id)]
