# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolScholarshipAwardSchedule(models.Model):
    """
    Represents one realization period of an award's Benefit line.
    A schedule line pins down exactly when a deduction is due, how
    much of the billing component it covers (``base_amount``,
    matched from the linked Payment Term's detail lines), and how
    much this award plans to deduct in that period
    (``amount_planned``). Fee Reduction lines derive one schedule
    line per matching ``school_enrollment_payment_term``; Cash lines
    derive theirs from the Benefit line's own Periodicity instead,
    with no Payment Term. A later, out-of-scope module realizes a
    schedule line by posting the actual deduction and filling
    ``amount_realized``.
    """

    _name = "school_scholarship_award_schedule"
    _description = "School Scholarship Award Schedule"
    _order = "date, benefit_id, id"

    benefit_id = fields.Many2one(
        string="Benefit",
        comodel_name="school_scholarship_award_benefit",
        required=True,
        ondelete="cascade",
        help="Benefit line this schedule line realizes one period of.",
    )
    award_id = fields.Many2one(
        string="Award",
        comodel_name="school_scholarship_award",
        related="benefit_id.award_id",
        store=True,
        help="Scholarship award of the linked Benefit line, kept as a "
        "stored column so this model's own domains and record rules "
        "do not have to traverse through Benefit.",
    )
    name = fields.Char(
        string="Name",
        compute="_compute_name",
        store=True,
        compute_sudo=True,
        help="Display name: the linked Payment Term's Term name when "
        "one is set, otherwise this schedule line's Date.",
    )
    payment_term_id = fields.Many2one(
        string="Payment Term",
        comodel_name="school_enrollment_payment_term",
        ondelete="restrict",
        help="Enrollment payment term this schedule line realizes. "
        "Required for a Fee Reduction Benefit line, and must be "
        "empty for a Cash Benefit line.",
    )
    date = fields.Date(
        string="Date",
        required=True,
        help="Date this deduction is due: the linked Payment Term's "
        "Estimated Invoice Date for a Fee Reduction line, or a date "
        "derived from the Benefit line's Periodicity for a Cash "
        "line.",
    )
    base_amount = fields.Monetary(
        string="Base Amount",
        currency_field="currency_id",
        compute="_compute_base_amount",
        store=True,
        compute_sudo=True,
        help="Billing amount this schedule line's Computation is "
        "applied to: the sum of the linked Payment Term's detail "
        "lines matching the Benefit line's Product, or its Product "
        "Category when the Benefit line targets one. Zero when no "
        "Payment Term is linked.",
    )
    amount_planned = fields.Monetary(
        string="Amount Planned",
        currency_field="currency_id",
        compute="_compute_amount_planned",
        store=True,
        readonly=False,
        compute_sudo=True,
        help="Amount this schedule line plans to deduct: the Benefit "
        "line's Percentage of Base Amount, its Fixed Amount, or the "
        "full Base Amount, capped at the Benefit line's Max Amount "
        "per Period when that ceiling is above zero. Left untouched "
        "on recompute once manually edited -- see Amount Planned "
        "Manual.",
    )
    amount_planned_manual = fields.Boolean(
        string="Amount Planned Manual",
        readonly=True,
        help="Automatically set when a user edits Amount Planned "
        "directly, so that regenerating the schedule -- which only "
        "ever creates lines that do not exist yet -- is never "
        "mistaken for a reason to recompute this line back to its "
        "formula value.",
    )
    amount_realized = fields.Monetary(
        string="Amount Realized",
        currency_field="currency_id",
        default=0.0,
        readonly=True,
        help="Amount actually deducted for this schedule line. Filled "
        "by the deduction document, a later module out of this "
        "item's scope; always zero until then.",
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("scheduled", "Scheduled"),
            ("realized", "Realized"),
            ("skipped", "Skipped"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        help="Lifecycle of this schedule line. Deliberately a plain "
        "stored field, not computed: moving a line to Skipped is a "
        "human decision the system cannot infer on its own.",
    )
    payment_term_state = fields.Selection(
        string="Payment Term State",
        related="payment_term_id.state",
        store=True,
        compute_sudo=True,
        help="Billing status of the linked Payment Term.",
    )
    customer_invoice_id = fields.Many2one(
        string="# Customer Invoice",
        comodel_name="customer_invoice",
        related="payment_term_id.customer_invoice_id",
        store=True,
        compute_sudo=True,
        help="Customer invoice of the linked Payment Term, once one "
        "has been created for it.",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="award_id.company_currency_id",
        store=True,
        compute_sudo=True,
        help="Currency the Base Amount, Amount Planned, and Amount "
        "Realized fields are expressed in, following the award's "
        "Company Currency.",
    )
    note = fields.Char(
        string="Note",
        help="Free-form note about this schedule line.",
    )

    @api.depends("payment_term_id", "payment_term_id.name", "date")
    def _compute_name(self):
        """Derive a display name from the Payment Term, or the Date.

        :return: nothing; assigns ``name``
        """
        for record in self:
            result = ""
            if record.payment_term_id:
                result = record.payment_term_id.name
            elif record.date:
                result = fields.Date.to_string(record.date)
            record.name = result

    @api.depends(
        "payment_term_id",
        "payment_term_id.detail_ids.price_subtotal",
        "payment_term_id.detail_ids.product_id",
        "payment_term_id.detail_ids.product_category_id",
        "benefit_id.product_id",
        "benefit_id.product_category_id",
    )
    def _compute_base_amount(self):
        """Sum the Payment Term detail lines matching the Benefit's scope.

        Matches by ``product_id`` when the Benefit line has no
        Product Category (a single-Product benefit), or by the
        detail lines' own ``product_category_id`` when the Benefit
        line targets a Product Category instead.

        :return: nothing; assigns ``base_amount``
        """
        for record in self:
            result = 0.0
            term = record.payment_term_id
            benefit = record.benefit_id
            if term:
                if benefit.product_category_id:
                    details = term.detail_ids.filtered(
                        lambda line: line.product_category_id
                        == benefit.product_category_id
                    )
                else:
                    details = term.detail_ids.filtered(
                        lambda line: line.product_id == benefit.product_id
                    )
                result = sum(details.mapped("price_subtotal"))
            record.base_amount = result

    @api.depends(
        "base_amount",
        "benefit_id.computation",
        "benefit_id.percentage",
        "benefit_id.amount_fixed",
        "benefit_id.max_amount_per_period",
    )
    def _compute_amount_planned(self):
        """Apply the Benefit line's Computation to the Base Amount.

        Skips recomputation for a line flagged
        ``amount_planned_manual``: ``record.amount_planned`` is read
        first as the neutral starting value, which -- per Odoo's own
        compute machinery (``Field.compute_value``, which clears the
        "to compute" flag before invoking this method precisely so
        the old value can be read safely) -- fetches the previously
        stored value rather than re-entering this method, so a
        manually edited amount survives an unrelated dependency
        change (e.g. editing the Benefit line's Percentage) instead
        of being silently overwritten.

        :return: nothing; assigns ``amount_planned``
        """
        for record in self:
            result = record.amount_planned
            if not record.amount_planned_manual:
                benefit = record.benefit_id
                if benefit.computation == "percentage":
                    result = record.base_amount * benefit.percentage / 100.0
                elif benefit.computation == "fixed":
                    result = benefit.amount_fixed
                else:
                    result = record.base_amount
                if (
                    benefit.max_amount_per_period > 0.0
                    and result > benefit.max_amount_per_period
                ):
                    result = benefit.max_amount_per_period
            record.amount_planned = result

    @api.constrains("benefit_id", "payment_term_id")
    def _check_duplicate_benefit_payment_term(self):
        """Forbid two schedule lines sharing Benefit and Payment Term.

        Mirrors standard SQL unique-pair semantics, where two rows
        both holding an empty (``NULL``) Payment Term are not
        considered a duplicate pair: every Cash schedule line has an
        empty ``payment_term_id`` by design, and several of them may
        legitimately belong to the same Benefit line, one per
        period. Only an actually repeated, non-empty Payment Term is
        rejected.

        :raises ValidationError: when another schedule line of the
            same Benefit already uses the same, non-empty, Payment
            Term.
        """
        for record in self:
            if not record.payment_term_id:
                continue
            duplicate_count = self.search_count(
                [
                    ("id", "!=", record.id),
                    ("benefit_id", "=", record.benefit_id.id),
                    ("payment_term_id", "=", record.payment_term_id.id),
                ]
            )
            if duplicate_count > 0:
                error_message = """
Document Type: %s
Context: Configure award schedule
Database ID: %s
Problem: Payment Term '%s' is already scheduled for this Benefit line
Solution: Select a Payment Term not yet scheduled for this Benefit line
""" % (
                    self._description,
                    record.id,
                    record.payment_term_id.display_name,
                )
                raise ValidationError(_(error_message))

    @api.constrains("benefit_id", "payment_term_id")
    def _check_payment_term_required(self):
        """Require Payment Term for Fee Reduction, forbid it for Cash.

        :raises ValidationError: when the Benefit line's
            ``benefit_type`` is ``fee_reduction`` and
            ``payment_term_id`` is empty, or is ``cash`` and
            ``payment_term_id`` is set.
        """
        for record in self:
            benefit_type = record.benefit_id.benefit_type
            if benefit_type == "fee_reduction" and not record.payment_term_id:
                error_message = """
Document Type: %s
Context: Configure award schedule
Database ID: %s
Problem: Fee Reduction Benefit lines require a Payment Term
Solution: Select the Payment Term this schedule line realizes
""" % (
                    self._description,
                    record.id,
                )
                raise ValidationError(_(error_message))
            if benefit_type == "cash" and record.payment_term_id:
                error_message = """
Document Type: %s
Context: Configure award schedule
Database ID: %s
Problem: Cash Benefit lines must not carry a Payment Term
Solution: Clear the Payment Term of this schedule line
""" % (
                    self._description,
                    record.id,
                )
                raise ValidationError(_(error_message))

    @api.constrains("payment_term_id", "award_id")
    def _check_payment_term_enrollment(self):
        """Require the Payment Term to belong to the award's Enrollment.

        :raises ValidationError: when ``payment_term_id.enrollment_id``
            is set and differs from ``award_id.enrollment_id``.
        """
        for record in self:
            term = record.payment_term_id
            if (
                term
                and term.enrollment_id
                and term.enrollment_id != record.award_id.enrollment_id
            ):
                error_message = """
Document Type: %s
Context: Configure award schedule
Database ID: %s
Problem: Payment Term '%s' does not belong to the award's Enrollment
Solution: Select a Payment Term of the award's own Enrollment
""" % (
                    self._description,
                    record.id,
                    term.display_name,
                )
                raise ValidationError(_(error_message))

    @api.constrains("amount_planned")
    def _check_amount_planned(self):
        """Forbid a negative planned amount.

        :raises ValidationError: when ``amount_planned`` is below
            zero.
        """
        for record in self:
            if record.amount_planned < 0:
                error_message = """
Document Type: %s
Context: Configure award schedule
Database ID: %s
Problem: Amount Planned %s is negative
Solution: Enter an Amount Planned of zero or above
""" % (
                    self._description,
                    record.id,
                    record.amount_planned,
                )
                raise ValidationError(_(error_message))

    def write(self, vals):
        """Flag ``amount_planned_manual`` when Amount Planned is edited.

        Only a write reaching this method's ``vals`` counts as a
        manual edit: the ORM's stored-compute machinery updates a
        computed field's column directly, without ever calling this
        ``write()``, so a recompute can never be mistaken for a
        manual edit here.

        :param vals: values to write
        :return: whatever ``super().write()`` returns
        """
        if "amount_planned" in vals:
            vals = dict(vals, amount_planned_manual=True)
        return super().write(vals)
