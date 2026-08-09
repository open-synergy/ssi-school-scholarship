# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SchoolScholarshipProgram(models.Model):
    """
    Represents the scholarship award rule for a school in a given academic
    year.
    A program defines who is eligible (funding basis, grades), how many
    awards it may grant (quota, renewal), and which accounts/journals a
    scholarship awarded under it posts to. The accounting fields default
    from the selected Scholarship Type but may be overridden per program.
    ``quota_used``/``quota_available`` are placeholders that always
    compute to zero until the ``school_scholarship_award_funding`` model
    (a later item) is wired up.
    """

    _name = "school_scholarship_program"
    _inherit = ["mixin.master_data", "mixin.many2one_configurator"]
    _description = "School Scholarship Program"
    _order = "academic_year_id desc, sequence, id"

    sequence = fields.Integer(
        string="Sequence",
        default=5,
        required=True,
        help="Display order of the scholarship program within the same "
        "academic year. Lower values appear first in the list.",
    )
    type_id = fields.Many2one(
        string="Scholarship Type",
        comodel_name="school_scholarship_type",
        required=True,
        ondelete="restrict",
        help="Scholarship type this program follows. Selecting a type "
        "fills the accounting fields below with its defaults, which "
        "may then be overridden for this program.",
    )
    school_id = fields.Many2one(
        string="School",
        comodel_name="school",
        required=True,
        help="School this scholarship program applies to.",
    )
    academic_year_id = fields.Many2one(
        string="Academic Year",
        comodel_name="school_academic_year",
        required=True,
        help="Academic year this scholarship program applies to.",
    )
    funding_basis = fields.Selection(
        string="Funding Basis",
        selection=[
            ("merit", "Merit Based"),
            ("need", "Need Based"),
            ("hybrid", "Hybrid"),
            ("categorical", "Categorical"),
        ],
        default="need",
        required=True,
        help="Basis this program grants scholarships on: purely academic "
        "merit, financial need, a hybrid of both, or a fixed "
        "category of beneficiary.",
    )
    grade_ids = fields.Many2many(
        string="Grades",
        comodel_name="school_grade",
        relation="rel_school_scholarship_program_2_grade",
        column1="program_id",
        column2="grade_id",
        help="Grades eligible for this program. Leave empty to make "
        "every grade eligible.",
    )
    funding_source_ids = fields.Many2many(
        string="Funding Sources",
        comodel_name="school_scholarship_funding_source",
        relation="rel_school_scholarship_program_2_funding_source",
        column1="program_id",
        column2="funding_source_id",
        required=True,
        help="Funding sources an award granted under this program may " "draw from.",
    )
    quota = fields.Integer(
        string="Quota",
        default=0,
        help="Maximum number of awards this program may grant. Zero "
        "means there is no quota.",
    )
    is_renewable = fields.Boolean(
        string="Is Renewable",
        default=False,
        help="Check this if an award granted under this program may be "
        "renewed into a following academic year.",
    )
    max_renewal = fields.Integer(
        string="Max Renewal",
        default=0,
        help="Maximum number of times an award granted under this "
        "program may be renewed. Only relevant when Is Renewable is "
        "checked.",
    )
    is_employee_benefit = fields.Boolean(
        string="Is Employee Benefit",
        default=False,
        help="Whether an award granted under this program is an "
        "employee benefit rather than a regular scholarship. "
        "Defaulted from the selected Scholarship Type, but may be "
        "overridden for this program.",
    )
    allow_asymmetric_recognition = fields.Boolean(
        string="Allow Asymmetric Recognition",
        default=False,
        help="Explicit opt-in for a foundation that intentionally defers "
        "the deduction/expense recognition of an award without "
        "deferring the related revenue recognition. Leave unchecked "
        "unless this asymmetry is intended.",
    )
    description = fields.Html(
        string="Description",
        help="Description of this scholarship program.",
    )
    deduction_journal_id = fields.Many2one(
        string="Deduction Journal",
        comodel_name="account.journal",
        required=True,
        ondelete="restrict",
        help="Journal used to post the scholarship deduction (discount) "
        "entry on the student invoice. Defaulted from the selected "
        "Scholarship Type.",
    )
    discount_account_id = fields.Many2one(
        string="Discount Account",
        comodel_name="account.account",
        required=True,
        ondelete="restrict",
        help="Contra-revenue account the scholarship deduction is booked "
        "to. Defaulted from the selected Scholarship Type.",
    )
    employee_benefit_account_id = fields.Many2one(
        string="Employee Benefit Account",
        comodel_name="account.account",
        ondelete="restrict",
        help="Employee benefit expense account used instead of the "
        "Discount Account when this program is flagged as an "
        "employee benefit. Defaulted from the selected Scholarship "
        "Type.",
    )
    disbursement_journal_id = fields.Many2one(
        string="Disbursement Journal",
        comodel_name="account.journal",
        ondelete="restrict",
        help="Journal used to post the cash disbursement entry when the "
        "scholarship is paid out to the student instead of deducted "
        "from the invoice. Defaulted from the selected Scholarship "
        "Type.",
    )
    expense_account_id = fields.Many2one(
        string="Expense Account",
        comodel_name="account.account",
        ondelete="restrict",
        help="Expense account the cash scholarship disbursement is "
        "booked to. Defaulted from the selected Scholarship Type.",
    )
    payable_account_id = fields.Many2one(
        string="Payable Account",
        comodel_name="account.account",
        ondelete="restrict",
        help="Payable account used to record the school's obligation to "
        "the student before the cash scholarship is disbursed. "
        "Defaulted from the selected Scholarship Type.",
    )
    deferred_discount_account_id = fields.Many2one(
        string="Deferred Discount Account",
        comodel_name="account.account",
        ondelete="restrict",
        help="Asset account used to defer recognition of the scholarship "
        "deduction across periods. Defaulted from the selected "
        "Scholarship Type.",
    )
    deferred_expense_account_id = fields.Many2one(
        string="Deferred Expense Account",
        comodel_name="account.account",
        ondelete="restrict",
        help="Asset account used to defer recognition of the cash "
        "scholarship expense across periods. Defaulted from the "
        "selected Scholarship Type.",
    )
    recognition_journal_id = fields.Many2one(
        string="Recognition Journal",
        comodel_name="account.journal",
        ondelete="restrict",
        help="Journal used to post the periodic recognition entry that "
        "releases the deferred discount or deferred expense. "
        "Defaulted from the selected Scholarship Type.",
    )
    quota_used = fields.Integer(
        string="Quota Used",
        compute="_compute_quota_used",
        store=False,
        compute_sudo=True,
        help="Number of awards already granted under this program. "
        "Always zero for now: the award model this is derived from "
        "does not exist yet and is wired up in a later item.",
    )
    quota_available = fields.Integer(
        string="Quota Available",
        compute="_compute_quota_available",
        store=False,
        compute_sudo=True,
        help="Remaining number of awards this program may still grant. "
        "Always zero for now: the award model this is derived from "
        "does not exist yet and is wired up in a later item.",
    )

    @api.depends()
    def _compute_quota_used(self):
        """Return zero until the award model exists.

        No real dependency: the ``school_scholarship_award_funding``
        model this should be derived from is not part of this item's
        scope, so the value is a fixed placeholder wired up in a
        later item.

        :return: nothing; assigns ``quota_used``
        """
        for record in self:
            record.quota_used = 0

    @api.depends()
    def _compute_quota_available(self):
        """Return zero until the award model exists.

        No real dependency: the ``school_scholarship_award_funding``
        model this should be derived from is not part of this item's
        scope, so the value is a fixed placeholder wired up in a
        later item.

        :return: nothing; assigns ``quota_available``
        """
        for record in self:
            record.quota_available = 0

    @api.onchange("type_id")
    def onchange_deduction_journal_id(self):
        """Default the Deduction Journal from the selected type."""
        self.deduction_journal_id = False
        if self.type_id:
            self.deduction_journal_id = self.type_id.deduction_journal_id

    @api.onchange("type_id")
    def onchange_discount_account_id(self):
        """Default the Discount Account from the selected type."""
        self.discount_account_id = False
        if self.type_id:
            self.discount_account_id = self.type_id.discount_account_id

    @api.onchange("type_id")
    def onchange_employee_benefit_account_id(self):
        """Default the Employee Benefit Account from the selected type."""
        self.employee_benefit_account_id = False
        if self.type_id:
            self.employee_benefit_account_id = self.type_id.employee_benefit_account_id

    @api.onchange("type_id")
    def onchange_disbursement_journal_id(self):
        """Default the Disbursement Journal from the selected type."""
        self.disbursement_journal_id = False
        if self.type_id:
            self.disbursement_journal_id = self.type_id.disbursement_journal_id

    @api.onchange("type_id")
    def onchange_expense_account_id(self):
        """Default the Expense Account from the selected type."""
        self.expense_account_id = False
        if self.type_id:
            self.expense_account_id = self.type_id.expense_account_id

    @api.onchange("type_id")
    def onchange_payable_account_id(self):
        """Default the Payable Account from the selected type."""
        self.payable_account_id = False
        if self.type_id:
            self.payable_account_id = self.type_id.payable_account_id

    @api.onchange("type_id")
    def onchange_deferred_discount_account_id(self):
        """Default the Deferred Discount Account from the selected type."""
        self.deferred_discount_account_id = False
        if self.type_id:
            self.deferred_discount_account_id = (
                self.type_id.deferred_discount_account_id
            )

    @api.onchange("type_id")
    def onchange_deferred_expense_account_id(self):
        """Default the Deferred Expense Account from the selected type."""
        self.deferred_expense_account_id = False
        if self.type_id:
            self.deferred_expense_account_id = self.type_id.deferred_expense_account_id

    @api.onchange("type_id")
    def onchange_recognition_journal_id(self):
        """Default the Recognition Journal from the selected type."""
        self.recognition_journal_id = False
        if self.type_id:
            self.recognition_journal_id = self.type_id.recognition_journal_id

    @api.onchange("type_id")
    def onchange_is_employee_benefit(self):
        """Default Is Employee Benefit from the selected type."""
        self.is_employee_benefit = False
        if self.type_id:
            self.is_employee_benefit = self.type_id.is_employee_benefit
