# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolScholarshipDeductionAllocation(models.Model):
    """
    Extends School Scholarship Deduction - Allocation, rejecting an
    allocation whose Customer Invoice belongs to a different
    Operating Unit than the parent Deduction document.

    ``customer_invoice_id``'s own domain is also narrowed to invoices
    of the parent Deduction's own Operating Unit -- a UI-level
    prevention on top of the data-level guard below.

    The ``@api.constrains`` guard can be bypassed on purpose by
    passing ``context={"school_scholarship_deduction_ou_skip_check":
    True}`` -- used only to build a test fixture that still gets
    caught by the header's own ``pre_open_action`` hook
    (``school_scholarship_deduction._10_check_allocation_operating_unit``),
    proving that second, independent guard actually works.
    """

    _name = "school_scholarship_deduction_allocation"
    _inherit = "school_scholarship_deduction_allocation"

    customer_invoice_id = fields.Many2one(
        domain="[('partner_id', '=', parent.partner_id), "
        "('state', '=', 'open'), ('amount_residual', '>', 0), "
        "('operating_unit_id', '=', parent.operating_unit_id)]",
    )

    @api.constrains("customer_invoice_id", "deduction_id")
    def _check_operating_unit(self):
        """Reject an allocation targeting a different Operating Unit.

        :raises ValidationError: when the selected Customer
            Invoice's own Operating Unit differs from the parent
            Deduction document's own Operating Unit.
        """
        if self.env.context.get("school_scholarship_deduction_ou_skip_check"):
            return
        for record in self:
            invoice_ou = record.customer_invoice_id.operating_unit_id
            deduction_ou = record.deduction_id.operating_unit_id
            if (
                record.customer_invoice_id
                and invoice_ou
                and deduction_ou
                and invoice_ou != deduction_ou
            ):
                error_message = """
Document Type: %s
Context: Configure deduction allocation
Database ID: %s
Problem: Invoice '%s' belongs to a different Operating Unit than this document
Solution: Select an invoice from the same Operating Unit as this document
""" % (
                    record._description,
                    record.id,
                    record.customer_invoice_id.display_name,
                )
                raise ValidationError(_(error_message))
