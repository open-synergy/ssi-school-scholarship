# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolScholarshipProgramScope(models.Model):
    """
    Represents one fee coverage line of a scholarship program.
    A scope line pins down exactly which billing component (a Product or
    a Product Category) a program's benefit applies to, how the benefit
    amount is computed, and how often it recurs. Together, the scope
    lines of a program answer the question a plain "free" label cannot
    answer: free of *what*, exactly.
    """

    _name = "school_scholarship_program_scope"
    _description = "School Scholarship Program Scope"
    _order = "sequence, id"

    program_id = fields.Many2one(
        string="Program",
        comodel_name="school_scholarship_program",
        required=True,
        ondelete="cascade",
        help="Scholarship program this scope line belongs to.",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=5,
        help="Display order of this scope line within the program.",
    )
    scope_basis = fields.Selection(
        string="Scope Basis",
        selection=[
            ("product", "Product"),
            ("product_category", "Product Category"),
        ],
        default="product",
        required=True,
        help="Whether this line targets a single Product or an entire "
        "Product Category.",
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
        help="Product this scope line covers. Required, and exclusive "
        "with Product Category, when Scope Basis is Product.",
    )
    product_category_id = fields.Many2one(
        string="Product Category",
        comodel_name="product.category",
        help="Product category this scope line covers. Required, and "
        "exclusive with Product, when Scope Basis is Product "
        "Category.",
    )
    benefit_type = fields.Selection(
        string="Benefit Type",
        selection=[
            ("fee_reduction", "Fee Reduction"),
            ("cash", "Cash"),
        ],
        default="fee_reduction",
        required=True,
        help="Whether the benefit reduces the billed fee directly, or "
        "is paid out to the student as cash.",
    )
    computation = fields.Selection(
        string="Computation",
        selection=[
            ("percentage", "Percentage"),
            ("fixed", "Fixed Amount"),
            ("full", "Full Coverage"),
        ],
        default="percentage",
        required=True,
        help="How the benefit amount is computed: a percentage of the "
        "billing component, a fixed amount, or full coverage.",
    )
    percentage = fields.Float(
        string="Percentage",
        digits=(5, 2),
        default=0.0,
        help="Percentage of the billing component covered by this "
        "line. Must be above 0 and at most 100 when Computation is "
        "Percentage.",
    )
    amount_fixed = fields.Monetary(
        string="Fixed Amount",
        currency_field="currency_id",
        default=0.0,
        help="Fixed amount covered by this line when Computation is " "Fixed Amount.",
    )
    max_amount_per_period = fields.Monetary(
        string="Max Amount per Period",
        currency_field="currency_id",
        default=0.0,
        help="Ceiling this line may cover in a single period. Zero "
        "means there is no ceiling.",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="program_id.deduction_journal_id.company_id.currency_id",
        store=True,
        help="Currency the Fixed Amount and Max Amount per Period "
        "fields are expressed in. The program does not carry its own "
        "Currency, so this follows the company of the program's "
        "required Deduction Journal.",
    )
    periodicity = fields.Selection(
        string="Periodicity",
        selection=[
            ("per_payment_term", "Per Payment Term"),
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("semester", "Semester"),
            ("one_time", "One Time"),
        ],
        default="per_payment_term",
        required=True,
        help="How often this line's benefit recurs. Fee Reduction "
        "lines are always tied to Per Payment Term, since their "
        "deduction schedule is derived from the payment term.",
    )

    @api.constrains("benefit_type", "periodicity")
    def _check_fee_reduction_periodicity(self):
        """Forbid a non-per-payment-term Periodicity on Fee Reduction.

        A Fee Reduction line's deduction schedule is derived from the
        student's payment term, so it is not allowed to carry a
        Periodicity calendar of its own.

        :raises ValidationError: when ``benefit_type`` is
            ``fee_reduction`` and ``periodicity`` is not
            ``per_payment_term``.
        """
        for record in self:
            if (
                record.benefit_type == "fee_reduction"
                and record.periodicity != "per_payment_term"
            ):
                error_message = """
Document Type: %s
Context: Configure scope periodicity
Database ID: %s
Problem: Fee Reduction requires Periodicity to be Per Payment Term
Solution: Select Per Payment Term, or change Benefit Type to Cash
""" % (
                    self._description,
                    record.id,
                )
                raise ValidationError(_(error_message))

    @api.constrains("scope_basis", "product_id", "product_category_id")
    def _check_scope_basis_target(self):
        """Require the target field matching ``scope_basis`` to be set.

        A Product scope must carry ``product_id`` and leave
        ``product_category_id`` empty, and a Product Category scope
        must carry ``product_category_id`` and leave ``product_id``
        empty, so that a scope line never targets two different
        billing components at once.

        :raises ValidationError: when the target field required by
            ``scope_basis`` is empty, or the unused one is filled.
        """
        for record in self:
            if record.scope_basis == "product" and (
                not record.product_id or record.product_category_id
            ):
                error_message = """
Document Type: %s
Context: Configure scope target
Database ID: %s
Problem: Scope Basis Product requires Product and no Product Category
Solution: Select a Product and clear Product Category
""" % (
                    self._description,
                    record.id,
                )
                raise ValidationError(_(error_message))
            if record.scope_basis == "product_category" and (
                not record.product_category_id or record.product_id
            ):
                error_message = """
Document Type: %s
Context: Configure scope target
Database ID: %s
Problem: Scope Basis Product Category requires Product Category and no Product
Solution: Select a Product Category and clear Product
""" % (
                    self._description,
                    record.id,
                )
                raise ValidationError(_(error_message))

    @api.constrains("computation", "percentage")
    def _check_percentage_range(self):
        """Require ``percentage`` above 0 and at most 100 when computed.

        :raises ValidationError: when ``computation`` is
            ``percentage`` and ``percentage`` is not strictly above 0
            and at most 100.
        """
        for record in self:
            if record.computation == "percentage" and not (
                0 < record.percentage <= 100
            ):
                error_message = """
Document Type: %s
Context: Configure scope computation
Database ID: %s
Problem: Percentage must be above 0 and at most 100
Solution: Enter a Percentage value between 0 (exclusive) and 100
""" % (
                    self._description,
                    record.id,
                )
                raise ValidationError(_(error_message))

    @api.constrains("program_id", "product_id", "product_category_id")
    def _check_duplicate_target(self):
        """Forbid two scope lines of the same program sharing a target.

        Checked with ``search_count`` rather than ``_sql_constraints``
        so the message can be raised without a bare database
        exception, and so it can be worded around the offending
        Product/Product Category rather than a column name.

        :raises ValidationError: when another scope line of the same
            program already targets the same ``product_id``, or the
            same ``product_category_id``.
        """
        for record in self:
            if not record.product_id and not record.product_category_id:
                # Neither target is set. ``_check_scope_basis_target``
                # (triggered together, since ``program_id`` is always
                # part of the written values) already rejects this
                # state, so there is no target to check here.
                continue
            if record.product_id:
                domain = [
                    ("id", "!=", record.id),
                    ("program_id", "=", record.program_id.id),
                    ("product_id", "=", record.product_id.id),
                ]
            else:
                domain = [
                    ("id", "!=", record.id),
                    ("program_id", "=", record.program_id.id),
                    (
                        "product_category_id",
                        "=",
                        record.product_category_id.id,
                    ),
                ]
            duplicate_count = self.search_count(domain)
            if duplicate_count > 0:
                error_message = """
Document Type: %s
Context: Configure scope target
Database ID: %s
Problem: Another scope line of this program already covers the same target
Solution: Select a Product or Product Category not yet covered by this program
""" % (
                    self._description,
                    record.id,
                )
                raise ValidationError(_(error_message))
