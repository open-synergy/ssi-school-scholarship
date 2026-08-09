# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SchoolScholarshipAwardBenefit(models.Model):
    """
    Represents one benefit line of a scholarship award.
    A benefit line either copies its terms from a program's Scope line
    (``scope_id``), or is entered ad hoc for a benefit not tied to any
    configured scope. Its ``price_subtotal`` (from the inherited
    ``mixin.product_line_account``) is the amount this line
    contributes to the award's ``amount_awarded``.
    """

    _name = "school_scholarship_award_benefit"
    _inherit = [
        "mixin.product_line_account",
    ]
    _description = "School Scholarship Award Benefit"
    _order = "sequence, id"

    award_id = fields.Many2one(
        string="Award",
        comodel_name="school_scholarship_award",
        required=True,
        ondelete="cascade",
        help="Scholarship award this benefit line belongs to.",
    )
    scope_id = fields.Many2one(
        string="Scope",
        comodel_name="school_scholarship_program_scope",
        help="Program scope line this benefit line is based on. "
        "Selecting it fills the rest of this line's fields; leave "
        "empty for an ad hoc benefit not tied to any configured "
        "scope.",
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
    product_id = fields.Many2one(
        required=True,
        help="Product this benefit line covers. Defaulted from the "
        "selected Scope when its Scope Basis is Product.",
    )
    product_category_id = fields.Many2one(
        string="Product Category",
        comodel_name="product.category",
        related=False,
        help="Product category this benefit line covers. Defaulted "
        "from the selected Scope when its Scope Basis is Product "
        "Category; left empty for a line covering a single Product.",
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
        "line. Only relevant when Computation is Percentage.",
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
        help="How often this line's benefit recurs.",
    )
    schedule_ids = fields.One2many(
        string="Schedule",
        comodel_name="school_scholarship_award_schedule",
        inverse_name="benefit_id",
        help="Schedule lines realizing this benefit line, one per "
        "matching Payment Term (Fee Reduction) or period "
        "(Cash).",
    )
    account_id = fields.Many2one(
        compute="_compute_account_id",
        store=True,
        compute_sudo=True,
        readonly=False,
        # ``mixin.product_line_account`` declares this field
        # ``required=True`` at the DB level. Odoo's ``create()`` never
        # includes a stored *computed* field's value in the initial
        # INSERT (it is filled by a follow-up UPDATE once the compute
        # runs), so keeping the inherited NOT NULL constraint makes
        # every create() fail before ``_compute_account_id`` ever
        # executes. The compute always assigns a real account, so the
        # DB-level requirement is redundant and must be relaxed here.
        required=False,
        help="Accounting account this line posts to when a later "
        "document realizes it: the award's Employee Benefit Account "
        "when the award is flagged as an employee benefit, the "
        "award's Expense Account when Benefit Type is Cash, "
        "otherwise the award's Discount Account.",
    )

    @api.depends(
        "award_id.is_employee_benefit",
        "award_id.employee_benefit_account_id",
        "award_id.expense_account_id",
        "award_id.discount_account_id",
        "benefit_type",
    )
    def _compute_account_id(self):
        """Derive the posting account from the award and benefit type.

        :return: nothing; assigns ``account_id``
        """
        for record in self:
            award = record.award_id
            if award.is_employee_benefit:
                record.account_id = award.employee_benefit_account_id
            elif record.benefit_type == "cash":
                record.account_id = award.expense_account_id
            else:
                record.account_id = award.discount_account_id

    @api.onchange("scope_id")
    def onchange_benefit_type(self):
        """Copy Benefit Type from the selected scope."""
        self.benefit_type = "fee_reduction"
        if self.scope_id:
            self.benefit_type = self.scope_id.benefit_type

    @api.onchange("scope_id")
    def onchange_product_id(self):
        """Copy Product from the selected scope when scoped by Product."""
        self.product_id = False
        if self.scope_id and self.scope_id.scope_basis == "product":
            self.product_id = self.scope_id.product_id

    @api.onchange("scope_id")
    def onchange_product_category_id(self):
        """Copy Product Category from a Product-Category-based scope."""
        self.product_category_id = False
        if self.scope_id and self.scope_id.scope_basis == "product_category":
            self.product_category_id = self.scope_id.product_category_id

    @api.onchange("scope_id")
    def onchange_computation(self):
        """Copy Computation from the selected scope."""
        self.computation = "percentage"
        if self.scope_id:
            self.computation = self.scope_id.computation

    @api.onchange("scope_id")
    def onchange_percentage(self):
        """Copy Percentage from the selected scope."""
        self.percentage = 0.0
        if self.scope_id:
            self.percentage = self.scope_id.percentage

    @api.onchange("scope_id")
    def onchange_amount_fixed(self):
        """Copy Fixed Amount from the selected scope."""
        self.amount_fixed = 0.0
        if self.scope_id:
            self.amount_fixed = self.scope_id.amount_fixed

    @api.onchange("scope_id")
    def onchange_max_amount_per_period(self):
        """Copy Max Amount per Period from the selected scope."""
        self.max_amount_per_period = 0.0
        if self.scope_id:
            self.max_amount_per_period = self.scope_id.max_amount_per_period

    @api.onchange("scope_id")
    def onchange_periodicity(self):
        """Copy Periodicity from the selected scope."""
        self.periodicity = "per_payment_term"
        if self.scope_id:
            self.periodicity = self.scope_id.periodicity
