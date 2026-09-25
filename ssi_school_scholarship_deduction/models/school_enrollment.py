# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round


class SchoolEnrollment(models.Model):
    # Extension: also rejects finishing this enrollment while a
    # scholarship deduction targeting one of its own invoices is not
    # yet Open, and adds each open, enrollment-mode scholarship
    # deduction's own share of Revenue Recognition Lines.

    _name = "school_enrollment"
    _inherit = [
        "school_enrollment",
    ]

    def _check_revenue_recognition_readiness(self):
        """Also reject a not-yet-open deduction on one of this
        enrollment's own invoices.

        A scholarship deduction still ``draft``/``confirm`` has not
        set its own final Recognition Method yet, so letting this
        enrollment finish first would let that deduction later open
        as ``immediate`` -- deferring the enrollment's own revenue
        without ever deferring the matching discount.

        :raises UserError: per ``super()``, or when an allocation of
            a ``draft``/``confirm`` ``school_scholarship_deduction``
            targets one of this enrollment's own invoices
        :return: nothing
        """
        super()._check_revenue_recognition_readiness()
        self.ensure_one()
        invoice_ids = self.payment_term_ids.mapped("customer_invoice_id").ids
        if not invoice_ids:
            return
        Allocation = self.env[  # pylint: disable=invalid-name
            "school_scholarship_deduction_allocation"
        ]
        draft_allocations = Allocation.sudo().search(
            [
                ("customer_invoice_id", "in", invoice_ids),
                ("deduction_id.state", "in", ("draft", "confirm")),
            ],
            limit=1,
        )
        if draft_allocations:
            deduction = draft_allocations.deduction_id
            error_message = (
                _(
                    """
Context: Finish enrollment
Database ID: %s
Problem: Scholarship deduction '%s' on this enrollment's own invoice is not yet Open
Solution: Confirm and approve that deduction before finishing this enrollment
"""
                )
                % (self.id, deduction.name)
            )
            raise UserError(error_message)

    def _prepare_revenue_recognition_line_data(self):
        """Also add one line per open, enrollment-mode deduction line.

        For every ``school_scholarship_deduction`` that is Open,
        carries Recognition Method ``enrollment``, and has at least
        one Allocation against one of this enrollment's own invoices,
        adds one Recognition Line per Deduction Line, scaled by the
        ratio of the Amount Allocated against this enrollment's own
        invoices over the deduction's own Amount Total. The amount is
        negated -- ``mixin.account_move_double_line`` reads a
        negative amount as reversing which side each account posts
        to, so this debits the Deduction Line's own Final Account and
        credits back the temporary account the deduction line itself
        already debited when it was opened.

        :return: list of dict of
            ``school_enrollment_revenue_recognition_line`` values
        """
        result = super()._prepare_revenue_recognition_line_data()
        self.ensure_one()
        invoice_ids = self.payment_term_ids.mapped("customer_invoice_id").ids
        if not invoice_ids:
            return result
        Deduction = self.env[  # pylint: disable=invalid-name
            "school_scholarship_deduction"
        ]
        deductions = Deduction.sudo().search(
            [
                ("state", "=", "open"),
                ("recognition_method", "=", "enrollment"),
                ("allocation_ids.customer_invoice_id", "in", invoice_ids),
            ]
        )
        precision = self.company_currency_id.decimal_places
        for deduction in deductions:
            allocated = sum(
                allocation.amount_allocated
                for allocation in deduction.allocation_ids
                if allocation.customer_invoice_id.id in invoice_ids
            )
            if not deduction.amount_total or not allocated:
                continue
            ratio = allocated / deduction.amount_total
            for line in deduction.line_ids:
                amount = float_round(
                    -(line.price_subtotal * ratio),
                    precision_digits=precision,
                )
                result.append(
                    {
                        "enrollment_id": self.id,
                        "name": line.name,
                        "scholarship_deduction_line_id": line.id,
                        "debit_account_id": line.account_id.id,
                        "credit_account_id": line.final_account_id.id,
                        "analytic_account_id": line.analytic_account_id.id,
                        "partner_id": deduction.partner_id.id,
                        "amount": amount,
                    }
                )
        return result
