# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolScholarshipDeductionAllocation(models.Model):
    """
    Represents one customer invoice a scholarship deduction is
    reconciled against.
    An allocation line states how much of the deduction document's
    Amount Total (``amount_allocated``) is applied to a given open
    ``customer_invoice``, capped at that invoice's own residual. The
    header's ``_20_reconcile`` hook merges this line's own
    ``invoice_move_line_id`` with the header's
    ``receivable_move_line_id`` and calls ``reconcile()``, storing the
    resulting ``account.partial.reconcile`` here.
    """

    _name = "school_scholarship_deduction_allocation"
    _description = "School Scholarship Deduction - Allocation"
    _order = "deduction_id, id"

    deduction_id = fields.Many2one(
        string="# Deduction",
        comodel_name="school_scholarship_deduction",
        required=True,
        ondelete="cascade",
        help="Deduction document this allocation line belongs to.",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="deduction_id.currency_id",
        store=True,
        help="Currency of the parent document.",
    )
    customer_invoice_id = fields.Many2one(
        string="Customer Invoice",
        comodel_name="customer_invoice",
        required=True,
        ondelete="restrict",
        domain="[('partner_id', '=', parent.partner_id), "
        "('state', '=', 'open'), ('amount_residual', '>', 0)]",
        help="Open customer invoice this allocation reconciles "
        "against. Restricted to invoices of this document's own "
        "Partner with a positive residual.",
    )
    invoice_move_line_id = fields.Many2one(
        string="Invoice Receivable Move Line",
        comodel_name="account.move.line",
        related="customer_invoice_id.receivable_move_line_id",
        help="Receivable journal item of the selected invoice, "
        "reconciled against this document's own receivable journal "
        "item once this document is opened.",
    )
    invoice_residual = fields.Monetary(
        string="Invoice Residual",
        currency_field="currency_id",
        related="customer_invoice_id.amount_residual",
        help="Residual amount still outstanding on the selected "
        "invoice. Amount Allocated may not exceed this.",
    )
    invoice_account_id = fields.Many2one(
        string="Invoice Receivable Account",
        comodel_name="account.account",
        related="customer_invoice_id.receivable_account_id",
        help="Receivable account of the selected invoice. Must match "
        "this document's own Receivable Account, or opening this "
        "document is rejected.",
    )
    amount_allocated = fields.Monetary(
        string="Amount Allocated",
        currency_field="currency_id",
        required=True,
        help="Portion of this document's Amount Total applied to the "
        "selected invoice. May not exceed Invoice Residual.",
    )
    partial_reconcile_id = fields.Many2one(
        string="Partial Reconcile",
        comodel_name="account.partial.reconcile",
        readonly=True,
        copy=False,
        help="Reconciliation record created by the header's "
        "``_20_reconcile`` hook once this document is opened.",
    )

    @api.constrains("amount_allocated", "invoice_residual")
    def _check_amount_allocated(self):
        """Forbid allocating more than the invoice's own residual.

        This is the same amount kept as a hard requirement by the
        header's own ``_05_check_reconcilable`` pre-open hook; this
        constrain rejects it earlier, at line entry time.

        :raises ValidationError: when ``amount_allocated`` exceeds
            ``invoice_residual``.
        """
        for record in self:
            if record.amount_allocated > record.invoice_residual:
                error_message = """
Document Type: %s
Context: Configure deduction allocation
Database ID: %s
Problem: Amount Allocated %s exceeds the invoice's residual %s
Solution: Lower the Amount Allocated to the invoice's own residual
""" % (
                    self._description,
                    record.id,
                    record.amount_allocated,
                    record.invoice_residual,
                )
                raise ValidationError(_(error_message))

    @api.constrains("customer_invoice_id", "deduction_id")
    def _check_duplicate_customer_invoice(self):
        """Forbid the same invoice appearing twice on one document.

        :raises ValidationError: when another allocation line of the
            same deduction document already targets the same invoice.
        """
        for record in self:
            duplicate_count = self.search_count(
                [
                    ("id", "!=", record.id),
                    ("deduction_id", "=", record.deduction_id.id),
                    ("customer_invoice_id", "=", record.customer_invoice_id.id),
                ]
            )
            if duplicate_count > 0:
                error_message = """
Document Type: %s
Context: Configure deduction allocation
Database ID: %s
Problem: Invoice '%s' is already allocated on this document
Solution: Select an invoice not yet allocated on this document, or remove the duplicate line
""" % (
                    self._description,
                    record.id,
                    record.customer_invoice_id.display_name,
                )
                raise ValidationError(_(error_message))
