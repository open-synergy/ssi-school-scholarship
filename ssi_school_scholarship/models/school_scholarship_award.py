# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date as datetime_date

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.ssi_decorator import ssi_decorator


class SchoolScholarshipAward(models.Model):
    """
    Represents the commitment of a scholarship program to a single
    student for a range of periods.
    An award is a commitment, not an accounting event: it never posts a
    journal entry of its own (there is deliberately no ``move_id`` on
    this model). The deduction it represents is recognised together
    with the revenue it reduces, i.e. when the period is billed — a
    later, per-period document (out of this item's scope) does the
    actual posting. The award only carries the commitment amount
    (``amount_awarded``, derived from its Benefit lines), how that
    commitment is funded (Funding lines, capped at 100% of the award),
    and the supporting Letters. The award follows the standard SSI
    four-state workflow: Draft -> Confirm -> Approve -> Open, and can
    also reach Done or Cancel.
    """

    _name = "school_scholarship_award"
    _inherit = [
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_open",
        "mixin.transaction_confirm",
        "mixin.company_currency",
        "mixin.localdict",
    ]
    _description = "School Scholarship Award"
    _order = "date desc, id desc"

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "open"
    _approval_state = "confirm"
    _after_approved_method = "action_open"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True

    _statusbar_visible_label = "draft,confirm,open,done"
    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "done_ok",
        "cancel_ok",
        "restart_ok",
        "manual_number_ok",
        "generate_schedule_ok",
        "create_deduction_ok",
        "revoke_ok",
    ]
    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_done",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_reject",
        "dom_open",
        "dom_done",
        "dom_cancel",
    ]

    # Sequence attribute
    _create_sequence_state = "open"

    date = fields.Date(
        string="Date",
        default=lambda r: datetime_date.today(),
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="The date of the award document (the SK date). This is "
        "not an accounting date — the award never posts a journal "
        "entry of its own.",
    )
    program_id = fields.Many2one(
        string="Program",
        comodel_name="school_scholarship_program",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Scholarship program this award is granted under.",
    )
    type_id = fields.Many2one(
        string="Scholarship Type",
        comodel_name="school_scholarship_type",
        related="program_id.type_id",
        store=True,
        readonly=True,
        help="Scholarship type of the selected program.",
    )
    student_id = fields.Many2one(
        string="Student",
        comodel_name="school_student",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Student this scholarship award is granted to.",
    )
    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        related="student_id.contact_id",
        store=True,
        help="The student's contact partner. Must match the partner "
        "billed on the student's invoices so the deduction created "
        "by a later document can be reconciled against it.",
    )
    enrollment_id = fields.Many2one(
        string="Enrollment",
        comodel_name="school_enrollment",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Enrollment this award is billed against. Must belong to "
        "the selected Student.",
    )
    school_id = fields.Many2one(
        string="School",
        comodel_name="school",
        related="enrollment_id.school_id",
        store=True,
        readonly=True,
        help="School of the selected enrollment.",
    )
    grade_id = fields.Many2one(
        string="Grade",
        comodel_name="school_grade",
        related="enrollment_id.grade_id",
        store=True,
        readonly=True,
        help="Grade of the selected enrollment.",
    )
    academic_year_id = fields.Many2one(
        string="Academic Year",
        comodel_name="school_academic_year",
        related="program_id.academic_year_id",
        store=True,
        readonly=True,
        help="Academic year of the selected program.",
    )
    date_start = fields.Date(
        string="Start Date",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="First period this award applies to.",
    )
    date_end = fields.Date(
        string="End Date",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Last period this award applies to. Must not be earlier "
        "than Start Date.",
    )
    benefit_ids = fields.One2many(
        string="Benefits",
        comodel_name="school_scholarship_award_benefit",
        inverse_name="award_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Benefit lines granted by this award. At least one line "
        "is required before this award can be confirmed.",
    )
    funding_ids = fields.One2many(
        string="Fundings",
        comodel_name="school_scholarship_award_funding",
        inverse_name="award_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Funding lines this award draws from. Their Percentage "
        "must add up to exactly 100%, and no Funding Source may "
        "appear more than once.",
    )
    letter_ids = fields.One2many(
        string="Letters",
        comodel_name="school_scholarship_letter",
        inverse_name="award_id",
        help="Letters related to this award (award letter, agreement, "
        "revocation, renewal). The physical file of each letter is "
        "attached on its chatter, not stored as a field.",
    )
    amount_awarded = fields.Monetary(
        string="Amount Awarded",
        currency_field="company_currency_id",
        compute="_compute_amount_awarded",
        store=True,
        compute_sudo=True,
        help="Total value of this award, computed as the sum of its "
        "Benefit lines.",
    )
    amount_realized = fields.Monetary(
        string="Amount Realized",
        currency_field="company_currency_id",
        compute="_compute_amount_realized",
        store=True,
        compute_sudo=True,
        help="Total amount of this award already realized through a "
        "per-period deduction. Always zero for now: the schedule "
        "model this is derived from is not part of this item's "
        "scope and is wired up in a later item.",
    )
    amount_remaining = fields.Monetary(
        string="Amount Remaining",
        currency_field="company_currency_id",
        compute="_compute_amount_remaining",
        store=True,
        compute_sudo=True,
        help="Amount Awarded not yet realized (Amount Awarded minus "
        "Amount Realized).",
    )
    compliance_state = fields.Selection(
        string="Compliance State",
        selection=[
            ("active", "Active"),
            ("warning", "Warning"),
            ("probation", "Probation"),
            ("suspended", "Suspended"),
            ("revoked", "Revoked"),
            ("completed", "Completed"),
        ],
        default="active",
        required=True,
        help="Ongoing compliance status of this award. Evaluation of "
        "this status is a later, Phase 3 item; here it is only "
        "recorded.",
    )
    renewal_of_award_id = fields.Many2one(
        string="Renewal Of",
        comodel_name="school_scholarship_award",
        readonly=True,
        help="Award this award is a renewal of, if any. The renewal "
        "mechanism itself (creating this link through a dedicated "
        "action) is a later, Phase 3 item; here it is only recorded.",
    )
    renewal_award_ids = fields.One2many(
        string="Renewals",
        comodel_name="school_scholarship_award",
        inverse_name="renewal_of_award_id",
        help="Awards that renew this award.",
    )
    renewal_sequence = fields.Integer(
        string="Renewal Sequence",
        compute="_compute_renewal_sequence",
        store=True,
        compute_sudo=True,
        help="How many times this award has been renewed, walking up "
        "the Renewal Of chain. Zero for an award that is not itself "
        "a renewal.",
    )
    is_employee_benefit = fields.Boolean(
        string="Is Employee Benefit",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Whether this award is an employee benefit rather than a "
        "regular scholarship. Defaulted from the selected Program, "
        "but may be overridden for this award.",
    )
    deduction_journal_id = fields.Many2one(
        string="Deduction Journal",
        comodel_name="account.journal",
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Journal used to post the scholarship deduction (discount) "
        "entry on the student invoice. Defaulted from the selected "
        "Program.",
    )
    discount_account_id = fields.Many2one(
        string="Discount Account",
        comodel_name="account.account",
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Contra-revenue account the scholarship deduction is "
        "booked to. Defaulted from the selected Program.",
    )
    employee_benefit_account_id = fields.Many2one(
        string="Employee Benefit Account",
        comodel_name="account.account",
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Employee benefit expense account used instead of the "
        "Discount Account when this award is flagged as an employee "
        "benefit. Defaulted from the selected Program.",
    )
    disbursement_journal_id = fields.Many2one(
        string="Disbursement Journal",
        comodel_name="account.journal",
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Journal used to post the cash disbursement entry when "
        "the scholarship is paid out to the student instead of "
        "deducted from the invoice. Defaulted from the selected "
        "Program.",
    )
    expense_account_id = fields.Many2one(
        string="Expense Account",
        comodel_name="account.account",
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Expense account the cash scholarship disbursement is "
        "booked to. Defaulted from the selected Program.",
    )
    payable_account_id = fields.Many2one(
        string="Payable Account",
        comodel_name="account.account",
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Payable account used to record the school's obligation to "
        "the student before the cash scholarship is disbursed. "
        "Defaulted from the selected Program.",
    )
    deferred_discount_account_id = fields.Many2one(
        string="Deferred Discount Account",
        comodel_name="account.account",
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Asset account used to defer recognition of the "
        "scholarship deduction across periods. Defaulted from the "
        "selected Program.",
    )
    deferred_expense_account_id = fields.Many2one(
        string="Deferred Expense Account",
        comodel_name="account.account",
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Asset account used to defer recognition of the cash "
        "scholarship expense across periods. Defaulted from the "
        "selected Program.",
    )
    recognition_journal_id = fields.Many2one(
        string="Recognition Journal",
        comodel_name="account.journal",
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Journal used to post the periodic recognition entry that "
        "releases the deferred discount or deferred expense. "
        "Defaulted from the selected Program.",
    )
    generate_schedule_ok = fields.Boolean(
        string="Can Generate Schedule",
        compute="_compute_policy",
        store=False,
        compute_sudo=True,
        help="Policy that determines whether the per-period deduction "
        "schedule may be generated for this award. The schedule "
        "generator itself is a later item; this policy field is "
        "wired up in advance.",
    )
    create_deduction_ok = fields.Boolean(
        string="Can Create Deduction",
        compute="_compute_policy",
        store=False,
        compute_sudo=True,
        help="Policy that determines whether a deduction document may "
        "be created from this award. The deduction document itself "
        "is out of this item's scope; this policy field is wired up "
        "in advance.",
    )
    revoke_ok = fields.Boolean(
        string="Can Revoke",
        compute="_compute_policy",
        store=False,
        compute_sudo=True,
        help="Policy that determines whether this award may be "
        "revoked. Revocation itself is a later, Phase 3 item; this "
        "policy field is wired up in advance.",
    )

    @api.depends("benefit_ids.price_subtotal")
    def _compute_amount_awarded(self):
        """Sum the benefit lines into the award's committed amount.

        :return: nothing; assigns ``amount_awarded``
        """
        for record in self:
            record.amount_awarded = sum(record.benefit_ids.mapped("price_subtotal"))

    @api.depends()
    def _compute_amount_realized(self):
        """Return zero until the schedule model exists.

        No real dependency: the per-period schedule model this should
        be derived from is not part of this item's scope, so the
        value is a fixed placeholder wired up in a later item.

        :return: nothing; assigns ``amount_realized``
        """
        for record in self:
            record.amount_realized = 0.0

    @api.depends("amount_awarded", "amount_realized")
    def _compute_amount_remaining(self):
        """Compute the still-uncommitted portion of the award.

        :return: nothing; assigns ``amount_remaining``
        """
        for record in self:
            record.amount_remaining = record.amount_awarded - record.amount_realized

    @api.depends("renewal_of_award_id", "renewal_of_award_id.renewal_sequence")
    def _compute_renewal_sequence(self):
        """Walk the ``renewal_of_award_id`` chain to count renewals.

        :return: nothing; assigns ``renewal_sequence``
        """
        for record in self:
            result = 0
            if record.renewal_of_award_id:
                result = record.renewal_of_award_id.renewal_sequence + 1
            record.renewal_sequence = result

    @api.onchange("program_id")
    def onchange_deduction_journal_id(self):
        """Default the Deduction Journal from the selected program."""
        self.deduction_journal_id = False
        if self.program_id:
            self.deduction_journal_id = self.program_id.deduction_journal_id

    @api.onchange("program_id")
    def onchange_discount_account_id(self):
        """Default the Discount Account from the selected program."""
        self.discount_account_id = False
        if self.program_id:
            self.discount_account_id = self.program_id.discount_account_id

    @api.onchange("program_id")
    def onchange_employee_benefit_account_id(self):
        """Default the Employee Benefit Account from the program."""
        self.employee_benefit_account_id = False
        if self.program_id:
            self.employee_benefit_account_id = (
                self.program_id.employee_benefit_account_id
            )

    @api.onchange("program_id")
    def onchange_disbursement_journal_id(self):
        """Default the Disbursement Journal from the selected program."""
        self.disbursement_journal_id = False
        if self.program_id:
            self.disbursement_journal_id = self.program_id.disbursement_journal_id

    @api.onchange("program_id")
    def onchange_expense_account_id(self):
        """Default the Expense Account from the selected program."""
        self.expense_account_id = False
        if self.program_id:
            self.expense_account_id = self.program_id.expense_account_id

    @api.onchange("program_id")
    def onchange_payable_account_id(self):
        """Default the Payable Account from the selected program."""
        self.payable_account_id = False
        if self.program_id:
            self.payable_account_id = self.program_id.payable_account_id

    @api.onchange("program_id")
    def onchange_deferred_discount_account_id(self):
        """Default the Deferred Discount Account from the program."""
        self.deferred_discount_account_id = False
        if self.program_id:
            self.deferred_discount_account_id = (
                self.program_id.deferred_discount_account_id
            )

    @api.onchange("program_id")
    def onchange_deferred_expense_account_id(self):
        """Default the Deferred Expense Account from the program."""
        self.deferred_expense_account_id = False
        if self.program_id:
            self.deferred_expense_account_id = (
                self.program_id.deferred_expense_account_id
            )

    @api.onchange("program_id")
    def onchange_recognition_journal_id(self):
        """Default the Recognition Journal from the selected program."""
        self.recognition_journal_id = False
        if self.program_id:
            self.recognition_journal_id = self.program_id.recognition_journal_id

    @api.onchange("program_id")
    def onchange_is_employee_benefit(self):
        """Default Is Employee Benefit from the selected program."""
        self.is_employee_benefit = False
        if self.program_id:
            self.is_employee_benefit = self.program_id.is_employee_benefit

    @api.constrains("date_start", "date_end")
    def _check_date_range(self):
        """Forbid an End Date earlier than the Start Date.

        :raises ValidationError: when ``date_end`` is set, ``date_start``
            is set, and ``date_end`` is earlier than ``date_start``.
        """
        for record in self:
            if (
                record.date_start
                and record.date_end
                and record.date_end < record.date_start
            ):
                error_message = """
Document Type: %s
Context: Set award period
Database ID: %s
Problem: End Date is earlier than Start Date
Solution: Select an End Date on or after Start Date
""" % (
                    self._description,
                    record.id,
                )
                raise ValidationError(_(error_message))

    @api.constrains("enrollment_id", "student_id")
    def _check_enrollment_student(self):
        """Require the Enrollment to belong to the selected Student.

        :raises ValidationError: when ``enrollment_id.student_id`` is
            not the same as ``student_id``.
        """
        for record in self:
            if (
                record.enrollment_id
                and record.student_id
                and record.enrollment_id.student_id != record.student_id
            ):
                error_message = """
Document Type: %s
Context: Select award enrollment
Database ID: %s
Problem: Enrollment '%s' does not belong to Student '%s'
Solution: Select an Enrollment that belongs to the selected Student
""" % (
                    self._description,
                    record.id,
                    record.enrollment_id.display_name,
                    record.student_id.name,
                )
                raise ValidationError(_(error_message))

    @api.constrains("company_currency_id", "enrollment_id")
    def _check_currency(self):
        """Require the award's currency to match the enrollment's.

        The award carries no standalone ``currency_id`` of its own —
        ``company_currency_id`` (from ``mixin.company_currency``) is
        the field the Benefit/Funding Monetary amounts are expressed
        in, and it must match the currency the enrollment is billed
        in for the eventual deduction to reconcile against the
        invoice.

        :raises ValidationError: when ``enrollment_id.currency_id`` is
            set and differs from ``company_currency_id``.
        """
        for record in self:
            if (
                record.enrollment_id
                and record.enrollment_id.currency_id
                and record.company_currency_id != record.enrollment_id.currency_id
            ):
                error_message = """
Document Type: %s
Context: Set award enrollment
Database ID: %s
Problem: Award currency '%s' does not match Enrollment currency '%s'
Solution: Select an Enrollment billed in the award's Company Currency
""" % (
                    self._description,
                    record.id,
                    record.company_currency_id.name,
                    record.enrollment_id.currency_id.name,
                )
                raise ValidationError(_(error_message))

    @api.constrains("renewal_sequence", "program_id")
    def _check_renewal_sequence(self):
        """Cap the renewal chain length at the program's Max Renewal.

        :raises ValidationError: when the program's ``max_renewal`` is
            above zero and ``renewal_sequence`` exceeds it.
        """
        for record in self:
            max_renewal = record.program_id.max_renewal
            if max_renewal > 0 and record.renewal_sequence > max_renewal:
                error_message = """
Document Type: %s
Context: Set award renewal
Database ID: %s
Problem: Renewal Sequence %s exceeds Program Max Renewal %s
Solution: Stop renewing this award, or increase Max Renewal on the Program
""" % (
                    self._description,
                    record.id,
                    record.renewal_sequence,
                    max_renewal,
                )
                raise ValidationError(_(error_message))

    @ssi_decorator.pre_confirm_action()
    def _10_check_benefit_line(self):
        """Reject confirming an award with no Benefit line.

        :raises UserError: when ``benefit_ids`` is empty.
        """
        self.ensure_one()
        if not self.benefit_ids:
            error_message = """
Document Type: %s
Context: Confirm award
Database ID: %s
Problem: Award has no Benefit line
Solution: Add at least one Benefit line before confirming
""" % (
                self._description,
                self.id,
            )
            raise UserError(_(error_message))

    @ssi_decorator.pre_cancel_action()
    def _10_check_realized_schedule(self):
        """Stub that always passes: no schedule model exists yet.

        The real check (forbidding cancellation once a period has
        been realized) is wired up in the schedule item, out of this
        item's scope.

        :return: ``True`` unconditionally
        """
        self.ensure_one()
        return True

    @api.model
    def _get_policy_field(self):
        """Register this model's policy fields for ``mixin.policy``.

        :return: the base policy fields plus this model's own
            ``generate_schedule_ok``, ``create_deduction_ok``, and
            ``revoke_ok``
        """
        res = super()._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "reject_ok",
            "restart_approval_ok",
            "done_ok",
            "cancel_ok",
            "restart_ok",
            "manual_number_ok",
            "generate_schedule_ok",
            "create_deduction_ok",
            "revoke_ok",
        ]
        res += policy_field
        return res

    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        """Reconfigure the statusbar's visible states on the form view.

        :param view_arch: the parsed form view architecture
        :return: the (possibly modified) view architecture
        """
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch
