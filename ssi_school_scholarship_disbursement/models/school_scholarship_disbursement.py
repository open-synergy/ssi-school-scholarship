# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date as datetime_date

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.ssi_decorator import ssi_decorator


class SchoolScholarshipDisbursement(models.Model):
    """
    Represents a cash scholarship disbursement posted as its own
    journal entry, then settled by an ``account.payment`` created
    outside this document.

    A disbursement document books its own ``account.move`` -- crediting
    the student's Payable Account on the header itself, and debiting
    each Disbursement Line's own expense account, carrying that line's
    own Analytic Account for its Funding source -- then simply waits
    for one or more ``account.payment`` records to be reconciled
    against its own Payable Move Line. This is the mirror image of
    ``school_scholarship_deduction``: there, the credited account is
    Receivable and it is reconciled against invoices already booked
    by this document; here, the credited account is Payable, and this
    document never books nor reconciles the payment itself -- a
    ``school_scholarship_payment_link`` row only records that link
    once the payment already exists. Opening this document also flips
    every realized Schedule line of the linked Award from
    ``scheduled`` to ``realized``; cancelling it reverses both the
    journal entry and that flip.

    Journal item labels never carry the student's name (see
    ``school_scholarship_disbursement_line._get_standard_label``):
    the scholarship recipient's identity is confidential, and the
    general ledger is read by anyone with ledger access, not just
    people cleared to see who receives a scholarship.
    """

    _name = "school_scholarship_disbursement"
    _inherit = [
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_open",
        "mixin.transaction_confirm",
        "mixin.company_currency",
        "mixin.account_move",
        "mixin.account_move_single_line",
    ]
    _description = "School Scholarship Disbursement"
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

    # Accounting Entry Header Mixin (``mixin.account_move``)
    _journal_id_field_name = "journal_id"
    _move_id_field_name = "move_id"
    _accounting_date_field_name = "date"
    _currency_id_field_name = "currency_id"
    _company_currency_id_field_name = "company_currency_id"

    # Accounting Move Single Line Mixin (``mixin.account_move_single_line``)
    # -- the header creates its own credit line to the Payable
    # Account, the reverse of ``customer_invoice``'s debit line to
    # Receivable, and the mirror of ``school_scholarship_deduction``'s
    # own credit line to Receivable.
    _account_id_field_name = "payable_account_id"
    _partner_id_field_name = "partner_id"
    _amount_currency_field_name = "amount_total"
    _date_field_name = "date"
    _label_field_name = "name"
    _need_date_due = True
    _date_due_field_name = "date_due"
    _normal_amount = "credit"

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
        help="Accounting date of this disbursement document.",
    )
    date_due = fields.Date(
        string="Date Due",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Due date recorded on the Payable Move Line created when "
        "this document is opened. May not precede Date.",
    )
    award_id = fields.Many2one(
        string="Award",
        comodel_name="school_scholarship_award",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Scholarship award this disbursement realizes.",
    )
    student_id = fields.Many2one(
        string="Student",
        comodel_name="school_student",
        related="award_id.student_id",
        help="Student of the selected Award.",
    )
    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        related="award_id.partner_id",
        store=True,
        help="The student's contact partner, credited by this "
        "document's own accounting entry.",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="company_currency_id",
        store=True,
        help="Currency this document is expressed in. This document "
        "does not support a currency other than the Company "
        "Currency.",
    )
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Accounting journal in which the resulting accounting "
        "entry of this document will be posted.",
    )
    payable_account_id = fields.Many2one(
        string="Payable Account",
        comodel_name="account.account",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Payable account credited for the total disbursement "
        "amount. Must allow reconciliation, or opening this document "
        "is rejected -- otherwise a later payment could never be "
        "matched against it.",
    )
    payment_method = fields.Selection(
        string="Payment Method",
        selection=[
            ("cash", "Cash"),
            ("bank_transfer", "Bank Transfer"),
        ],
        default="bank_transfer",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="How the student actually receives this disbursement. "
        "Bank Transfer requires a Bank Account to be selected below.",
    )
    bank_account_id = fields.Many2one(
        string="Bank Account",
        comodel_name="res.partner.bank",
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Bank account the disbursement is transferred to. "
        "Required while Payment Method is Bank Transfer.",
    )
    line_ids = fields.One2many(
        string="Lines",
        comodel_name="school_scholarship_disbursement_line",
        inverse_name="disbursement_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Disbursement lines, one per (Schedule line, Funding "
        "line) pairing. Their sum is this document's Amount Total.",
    )
    schedule_ids = fields.One2many(
        string="Realized Schedule",
        comodel_name="school_scholarship_award_schedule",
        inverse_name="disbursement_id",
        readonly=True,
        help="Award Schedule lines realized by this document. Filled "
        "when this document opens; cleared again if it is "
        "cancelled.",
    )
    amount_total = fields.Monetary(
        string="Amount Total",
        currency_field="currency_id",
        compute="_compute_amount_total",
        store=True,
        compute_sudo=True,
        help="Sum of the Disbursement lines' Price Subtotal. This is "
        "also the amount credited to the Payable Account.",
    )
    move_id = fields.Many2one(
        string="Move",
        comodel_name="account.move",
        readonly=True,
        copy=False,
        help="Journal entry generated when this document is opened.",
    )
    payable_move_line_id = fields.Many2one(
        string="Payable Move Line",
        comodel_name="account.move.line",
        readonly=True,
        copy=False,
        help="Journal item on the Payable Account created together "
        "with ``move_id``. Its own residual drives Amount Paid and "
        "Amount Residual below, once an ``account.payment`` is "
        "reconciled against it.",
    )
    amount_paid = fields.Monetary(
        string="Amount Paid",
        currency_field="currency_id",
        compute="_compute_amount_paid",
        store=True,
        compute_sudo=True,
        help="Portion of Amount Total already settled by a "
        "reconciled ``account.payment``, derived from the Payable "
        "Move Line's own residual amount.",
    )
    amount_residual = fields.Monetary(
        string="Amount Residual",
        currency_field="currency_id",
        compute="_compute_amount_paid",
        store=True,
        compute_sudo=True,
        help="Portion of Amount Total still outstanding on the "
        "Payable Move Line. Equal to Amount Total before any "
        "payment is reconciled.",
    )
    payment_ids = fields.One2many(
        string="Payments",
        comodel_name="school_scholarship_payment_link",
        inverse_name="disbursement_id",
        help="Links to the ``account.payment`` records that settle "
        "this document's own Payable Account. This document never "
        "creates a payment itself -- these rows only record a link "
        "to one that already exists.",
    )

    @api.depends("line_ids.price_subtotal")
    def _compute_amount_total(self):
        """Sum the Disbursement lines into this document's total.

        :return: nothing; assigns ``amount_total``
        """
        for record in self:
            record.amount_total = sum(record.line_ids.mapped("price_subtotal"))

    @api.depends(
        "payable_move_line_id.amount_residual_currency",
        "payable_move_line_id.reconciled",
        "amount_total",
    )
    def _compute_amount_paid(self):
        """Derive Amount Paid/Residual from the Payable Move Line.

        ``account.move.line.amount_residual_currency`` is signed by
        debit/credit orientation -- positive for a debit-normal line
        such as ``customer_invoice``'s own receivable line, negative
        for this document's own credit-normal payable line while it
        remains unreconciled. ``abs()`` normalizes it back to a plain
        outstanding amount, so Amount Residual reads as Amount Total
        before any payment is reconciled, exactly like
        ``customer_invoice``'s own Amount Residual reads before it is
        paid.

        :return: nothing; assigns ``amount_paid`` and
            ``amount_residual``
        """
        for record in self:
            amount_residual = 0.0
            amount_paid = 0.0
            if record.payable_move_line_id:
                amount_residual = abs(
                    record.payable_move_line_id.amount_residual_currency
                )
                amount_paid = record.amount_total - amount_residual
            record.amount_paid = amount_paid
            record.amount_residual = amount_residual

    @api.onchange("award_id")
    def onchange_journal_id(self):
        """Default Journal from the selected Award.

        :return: nothing
        """
        self.journal_id = False
        if self.award_id:
            self.journal_id = self.award_id.disbursement_journal_id

    @api.onchange("award_id")
    def onchange_payable_account_id(self):
        """Default Payable Account from the selected Award.

        :return: nothing
        """
        self.payable_account_id = False
        if self.award_id:
            self.payable_account_id = self.award_id.payable_account_id

    @api.constrains("payable_account_id")
    def _check_payable_account_reconcile(self):
        """Require the Payable Account to allow reconciliation.

        :raises ValidationError: when ``payable_account_id`` is set
            and its own ``reconcile`` is falsy.
        """
        for record in self:
            if record.payable_account_id and not record.payable_account_id.reconcile:
                error_message = """
Document Type: %s
Context: Configure disbursement
Database ID: %s
Problem: Payable Account '%s' does not allow reconciliation
Solution: Enable reconciliation on the Payable Account
""" % (
                    record._description,
                    record.id,
                    record.payable_account_id.display_name,
                )
                raise ValidationError(_(error_message))

    @api.constrains("payment_method", "bank_account_id")
    def _check_bank_account_required(self):
        """Require Bank Account while Payment Method is Bank Transfer.

        :raises ValidationError: when ``payment_method`` is
            ``bank_transfer`` and ``bank_account_id`` is empty.
        """
        for record in self:
            if record.payment_method == "bank_transfer" and not record.bank_account_id:
                error_message = """
Document Type: %s
Context: Configure disbursement
Database ID: %s
Problem: Bank Account is empty while Payment Method is Bank Transfer
Solution: Select a Bank Account, or set Payment Method to Cash
""" % (
                    record._description,
                    record.id,
                )
                raise ValidationError(_(error_message))

    @api.constrains("date", "date_due")
    def _check_date_due(self):
        """Forbid Date Due preceding Date.

        :raises ValidationError: when both ``date`` and ``date_due``
            are set and ``date_due`` is earlier than ``date``.
        """
        for record in self:
            if record.date and record.date_due and record.date_due < record.date:
                error_message = """
Document Type: %s
Context: Configure disbursement
Database ID: %s
Problem: Date Due is earlier than Date
Solution: Select a Date Due on or after Date
""" % (
                    record._description,
                    record.id,
                )
                raise ValidationError(_(error_message))

    @ssi_decorator.post_open_action()
    def _10_create_accounting_entry(self):
        """Create and post this document's ``account.move``.

        Creates the header move, this document's own credit line to
        the Payable Account (saved to ``payable_move_line_id``), a
        debit line per Disbursement Line, then posts the move.

        :return: nothing
        """
        self.ensure_one()
        self._create_standard_move()  # Mixin
        ml = self._create_standard_ml()  # Mixin
        self.write(
            {
                "payable_move_line_id": ml.id,
            }
        )
        for line in self.line_ids:
            line._create_standard_ml()  # Mixin
        self._post_standard_move()  # Mixin

    def _prepare_standard_move(self):
        """Add this document's Partner to the ``account.move`` header.

        :return: dict of ``account.move`` values
        """
        res = super()._prepare_standard_move()
        res["partner_id"] = getattr(self, self._partner_id_field_name).id
        return res

    @ssi_decorator.post_open_action()
    def _20_mark_schedule_realized(self):
        """Flip every realized Schedule line to state ``realized``.

        :return: nothing
        """
        self.ensure_one()
        schedules = self.line_ids.mapped("schedule_id")
        schedules.write(
            {
                "disbursement_id": self.id,
                "state": "realized",
            }
        )

    @ssi_decorator.post_cancel_action()
    def _10_delete_accounting_entry(self):
        """Delete this document's ``account.move``.

        :return: nothing
        """
        self.ensure_one()
        self._delete_standard_move()  # Mixin

    @ssi_decorator.post_cancel_action()
    def _20_reset_schedule(self):
        """Reset every realized Schedule line back to ``scheduled``.

        :return: nothing
        """
        self.ensure_one()
        self.schedule_ids.write(
            {
                "disbursement_id": False,
                "state": "scheduled",
            }
        )

    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        """Reconfigure the statusbar's visible states on the form view.

        :param view_arch: the parsed form view architecture
        :return: the (possibly modified) view architecture
        """
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch

    @api.model
    def _get_policy_field(self):
        """Register this model's policy fields for ``mixin.policy``.

        ``open_ok`` (from ``mixin.transaction_open``) must be listed
        here too -- see the identical note on
        ``school_scholarship_award._get_policy_field``.

        :return: the base policy fields of the standard four-mixin
            workflow combo
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
            "open_ok",
        ]
        res += policy_field
        return res
