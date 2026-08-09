# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date as datetime_date

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero

from odoo.addons.ssi_decorator import ssi_decorator


class SchoolScholarshipDeduction(models.Model):
    """
    Represents a scholarship deduction posted, and reconciled, on its
    own.
    A deduction document books its own ``account.move`` -- debiting a
    discount/expense account per Deduction Line and crediting the
    student's Receivable Account on the header itself -- then
    reconciles that credit against one or more open customer invoices
    (its Allocation lines), so the invoices' own ``amount_residual``
    drops and they move to Paid once fully covered. This is the
    reverse of ``customer_invoice``'s own accounting entry: there,
    the header debits Receivable; here, it credits it. Opening this
    document also flips every realized Schedule line of the linked
    Award from ``scheduled`` to ``realized``; cancelling it reverses
    both the reconciliation and that flip.

    When ``recognition_date`` (the start of the period the deduction
    actually pays for) falls after ``date`` (the accounting date of
    this document itself), the deduction spans a fiscal year
    boundary and ``recognition_method`` becomes ``deferred``: each
    Line then debits a temporary Deferred Account instead of its own
    Final Account, and a separate
    ``school_scholarship_deduction_recognition`` document later moves
    the amount from the Deferred Account to the Final Account, once
    or several times, as the underlying service is actually
    delivered.
    """

    _name = "school_scholarship_deduction"
    _inherit = [
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_open",
        "mixin.transaction_confirm",
        "mixin.company_currency",
        "mixin.account_move",
        "mixin.account_move_single_line",
    ]
    _description = "School Scholarship Deduction"
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
    # -- the header creates its own credit line to the Receivable
    # Account, the reverse of ``customer_invoice``'s debit line.
    _account_id_field_name = "receivable_account_id"
    _partner_id_field_name = "partner_id"
    _amount_currency_field_name = "amount_total"
    _date_field_name = "date"
    _label_field_name = "name"
    _need_date_due = False
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
        help="Accounting date of this deduction document.",
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
        help="Scholarship award this deduction realizes.",
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
        help="The student's contact partner. Must match the Partner "
        "of every allocated invoice.",
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
    receivable_account_id = fields.Many2one(
        string="Receivable Account",
        comodel_name="account.account",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Receivable account credited for the total deduction "
        "amount. Must be identical to the Receivable Account of "
        "every allocated invoice, or reconciliation fails when this "
        "document is opened.",
    )
    line_ids = fields.One2many(
        string="Lines",
        comodel_name="school_scholarship_deduction_line",
        inverse_name="deduction_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Deduction lines, one per (Schedule line, Funding line) "
        "pairing. Their sum is this document's Amount Total.",
    )
    allocation_ids = fields.One2many(
        string="Allocations",
        comodel_name="school_scholarship_deduction_allocation",
        inverse_name="deduction_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Customer invoices this deduction is reconciled against. "
        "Their Amount Allocated must add up to exactly this "
        "document's Amount Total before it can be opened.",
    )
    schedule_ids = fields.One2many(
        string="Realized Schedule",
        comodel_name="school_scholarship_award_schedule",
        inverse_name="deduction_id",
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
        help="Sum of the Deduction lines' Price Subtotal. This is "
        "also the amount credited to the Receivable Account.",
    )
    amount_allocated = fields.Monetary(
        string="Amount Allocated",
        currency_field="currency_id",
        compute="_compute_amount_allocated",
        store=True,
        compute_sudo=True,
        help="Sum of the Allocation lines' Amount Allocated.",
    )
    amount_unallocated = fields.Monetary(
        string="Amount Unallocated",
        currency_field="currency_id",
        compute="_compute_amount_unallocated",
        store=True,
        compute_sudo=True,
        help="Amount Total not yet assigned to an Allocation line. "
        "Must be zero before this document can be opened.",
    )
    move_id = fields.Many2one(
        string="Move",
        comodel_name="account.move",
        readonly=True,
        copy=False,
        help="Journal entry generated when this document is opened.",
    )
    receivable_move_line_id = fields.Many2one(
        string="Receivable Move Line",
        comodel_name="account.move.line",
        readonly=True,
        copy=False,
        help="Journal item on the Receivable Account created together "
        "with ``move_id``, then reconciled against every allocated "
        "invoice's own receivable journal item.",
    )
    reconciled = fields.Boolean(
        string="Reconciled",
        related="receivable_move_line_id.reconciled",
        store=True,
        compute_sudo=True,
        help="Technical flag mirroring whether the receivable journal "
        "item has been fully reconciled.",
    )
    recognition_method = fields.Selection(
        string="Recognition Method",
        selection=[
            ("immediate", "Immediate"),
            ("deferred", "Deferred"),
        ],
        compute="_compute_recognition_method",
        store=True,
        readonly=False,
        help="``Deferred`` once Recognition Date falls after this "
        "document's own Date -- meaning the service this deduction "
        "pays for has not started yet. Defaults automatically but "
        "may be overridden manually.",
    )
    recognition_date = fields.Date(
        string="Recognition Date",
        compute="_compute_recognition_date",
        store=True,
        readonly=False,
        help="Start of the period the underlying service is actually "
        "delivered -- the later of this document's own Date and the "
        "Award's own Start Date. Defaults automatically but may be "
        "overridden manually.",
    )
    deferred_account_id = fields.Many2one(
        string="Deferred Account",
        comodel_name="account.account",
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Temporary asset account each Line posts to instead of "
        "its own Final Account while Recognition Method is "
        "``Deferred``. Defaulted from the Award's own Deferred "
        "Discount Account. Required while Recognition Method is "
        "``Deferred``.",
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
        help="Journal a Recognition document of this deduction posts "
        "its entry to. Defaulted from the Award's own Recognition "
        "Journal.",
    )
    recognition_ids = fields.One2many(
        string="Recognitions",
        comodel_name="school_scholarship_deduction_recognition",
        inverse_name="deduction_id",
        readonly=True,
        help="Recognition documents that move this deduction's "
        "deferred amount from the Deferred Account to each Line's "
        "own Final Account.",
    )
    amount_recognized = fields.Monetary(
        string="Amount Recognized",
        currency_field="currency_id",
        compute="_compute_amount_recognized",
        store=True,
        compute_sudo=True,
        help="Sum of this deduction's own Recognition documents' "
        "Amount, counting only those in Done status.",
    )
    amount_deferred = fields.Monetary(
        string="Amount Deferred",
        currency_field="currency_id",
        compute="_compute_amount_deferred",
        store=True,
        compute_sudo=True,
        help="Amount Total not yet moved out of the Deferred Account "
        "by a Recognition document. Reaches zero once fully "
        "recognized.",
    )
    recognition_state = fields.Selection(
        string="Recognition Status",
        selection=[
            ("not_applicable", "Not Applicable"),
            ("pending", "Pending"),
            ("partial", "Partially Recognized"),
            ("recognized", "Recognized"),
        ],
        compute="_compute_recognition_state",
        store=True,
        compute_sudo=True,
        help="``Not Applicable`` while Recognition Method is "
        "``Immediate``; otherwise ``Pending`` before any Recognition "
        "is Done, ``Partially Recognized`` while Amount Recognized "
        "is below Amount Total, and ``Recognized`` once it reaches "
        "it.",
    )

    @api.depends("date", "recognition_date")
    def _compute_recognition_method(self):
        """Default Recognition Method from Date vs. Recognition Date.

        :return: nothing; assigns ``recognition_method``
        """
        for record in self:
            method = "immediate"
            if (
                record.date
                and record.recognition_date
                and record.recognition_date > record.date
            ):
                method = "deferred"
            record.recognition_method = method

    @api.depends("date", "award_id.date_start")
    def _compute_recognition_date(self):
        """Default Recognition Date from Date and the Award's Start Date.

        :return: nothing; assigns ``recognition_date``
        """
        for record in self:
            candidate = record.date
            if (
                record.award_id.date_start
                and record.date
                and record.award_id.date_start > record.date
            ):
                candidate = record.award_id.date_start
            record.recognition_date = candidate

    @api.depends("recognition_ids.amount", "recognition_ids.state")
    def _compute_amount_recognized(self):
        """Sum this deduction's own Done Recognition documents.

        :return: nothing; assigns ``amount_recognized``
        """
        for record in self:
            done_recognitions = record.recognition_ids.filtered(
                lambda recognition: recognition.state == "done"
            )
            record.amount_recognized = sum(done_recognitions.mapped("amount"))

    @api.depends("amount_total", "amount_recognized")
    def _compute_amount_deferred(self):
        """Compute the still-deferred portion of Amount Total.

        :return: nothing; assigns ``amount_deferred``
        """
        for record in self:
            record.amount_deferred = record.amount_total - record.amount_recognized

    @api.depends("recognition_method", "amount_total", "amount_recognized")
    def _compute_recognition_state(self):
        """Derive the Recognition Status from method and amounts.

        :return: nothing; assigns ``recognition_state``
        """
        for record in self:
            state = "not_applicable"
            if record.recognition_method == "deferred":
                precision = record.company_currency_id.decimal_places
                if float_is_zero(record.amount_recognized, precision_digits=precision):
                    state = "pending"
                elif (
                    float_compare(
                        record.amount_recognized,
                        record.amount_total,
                        precision_digits=precision,
                    )
                    >= 0
                ):
                    state = "recognized"
                else:
                    state = "partial"
            record.recognition_state = state

    @api.depends("line_ids.price_subtotal")
    def _compute_amount_total(self):
        """Sum the Deduction lines into this document's total.

        :return: nothing; assigns ``amount_total``
        """
        for record in self:
            record.amount_total = sum(record.line_ids.mapped("price_subtotal"))

    @api.depends("allocation_ids.amount_allocated")
    def _compute_amount_allocated(self):
        """Sum the Allocation lines' committed amount.

        :return: nothing; assigns ``amount_allocated``
        """
        for record in self:
            record.amount_allocated = sum(
                record.allocation_ids.mapped("amount_allocated")
            )

    @api.depends("amount_total", "amount_allocated")
    def _compute_amount_unallocated(self):
        """Compute the still-unassigned portion of Amount Total.

        :return: nothing; assigns ``amount_unallocated``
        """
        for record in self:
            record.amount_unallocated = record.amount_total - record.amount_allocated

    @api.onchange("allocation_ids")
    def onchange_receivable_account_id(self):
        """Default the Receivable Account from the first allocated invoice.

        Only fills the field when it is still empty -- matching
        ``01-create.md``'s own wording -- and only once the first
        Allocation line's invoice is actually selected. Unconditionally
        clearing it (the previous behaviour) fired on every
        ``allocation_ids`` change, including a bare row-add before any
        invoice is picked, blanking a value the user may have already
        typed on the header and racing the newly-added row's own
        onchange in the web client.

        Written as guard clauses -- rather than one compound ``and``
        condition -- so each only needs its own single variable
        exercised true/false for full branch coverage, instead of
        every combination of the compound expression's operands. The
        final assignment is unconditional rather than gated on
        ``invoice_account_id`` being truthy: by the time it runs, the
        guards above already guarantee ``receivable_account_id`` is
        empty, so assigning it another falsy value (the transient
        state right after a bare row-add, before its own Customer
        Invoice is picked) is a harmless no-op, not a regression --
        that transient state cannot be reproduced through
        ``odoo.tests.common.Form`` at all (its ``new()`` context only
        evaluates dependent onchanges once every value in the
        ``with`` block is set, never on the bare row in between), only
        through the real web client's own sequential RPCs.
        """
        if self.receivable_account_id:
            return
        if not self.allocation_ids:
            return
        self.receivable_account_id = self.allocation_ids[0].invoice_account_id

    @api.onchange("award_id")
    def onchange_deferred_account_id(self):
        """Default Deferred Account from the selected Award.

        :return: nothing
        """
        self.deferred_account_id = False
        if self.award_id:
            self.deferred_account_id = self.award_id.deferred_discount_account_id

    @api.onchange("award_id")
    def onchange_recognition_journal_id(self):
        """Default Recognition Journal from the selected Award.

        :return: nothing
        """
        self.recognition_journal_id = False
        if self.award_id:
            self.recognition_journal_id = self.award_id.recognition_journal_id

    @api.constrains("recognition_method", "deferred_account_id")
    def _check_deferred_account_required(self):
        """Require Deferred Account while Recognition Method is deferred.

        :raises ValidationError: when ``recognition_method`` is
            ``deferred`` and ``deferred_account_id`` is empty.
        """
        for record in self:
            if (
                record.recognition_method == "deferred"
                and not record.deferred_account_id
            ):
                error_message = """
Document Type: %s
Context: Configure deduction recognition
Database ID: %s
Problem: Deferred Account is empty while Recognition Method is Deferred
Solution: Select a Deferred Account, or set Recognition Method back to Immediate
""" % (
                    record._description,
                    record.id,
                )
                raise ValidationError(_(error_message))

    @api.constrains("recognition_method", "allocation_ids")
    def _check_recognition_symmetry(self):
        """Reject deferring the deduction without deferring the revenue.

        Deferring this deduction's own posting while the invoice it
        is allocated against still credits an Income-type account
        outright would inflate the current period's profit by the
        deferred discount, without deferring the matching revenue --
        unless the Award's own Program explicitly opts into that
        asymmetry.

        :raises ValidationError: when ``recognition_method`` is
            ``deferred``, the Program's own
            ``allow_asymmetric_recognition`` is falsy, and at least
            one allocated invoice has a Line posting to an
            Income-type account.
        """
        for record in self:
            if record.recognition_method != "deferred":
                continue
            if record.award_id.program_id.allow_asymmetric_recognition:
                continue
            invoices = record.allocation_ids.mapped("customer_invoice_id")
            income_lines = invoices.mapped("line_ids").filtered(
                lambda line: line.account_id.user_type_id.internal_group == "income"
            )
            if income_lines:
                error_message = """
Document Type: %s
Context: Configure deduction recognition
Database ID: %s
Problem: Deferred deduction but the allocated invoice recognizes revenue immediately
Solution: Enable Allow Asymmetric Recognition on the Program, or keep Method Immediate
""" % (
                    record._description,
                    record.id,
                )
                raise ValidationError(_(error_message))

    @ssi_decorator.pre_cancel_action()
    def _05_check_no_done_recognition(self):
        """Reject cancelling a deduction with a Done Recognition.

        :raises UserError: when at least one of this deduction's own
            Recognition documents is in Done status.
        """
        self.ensure_one()
        if self.recognition_ids.filtered(
            lambda recognition: recognition.state == "done"
        ):
            error_message = """
Document Type: %s
Context: Cancel deduction
Database ID: %s
Problem: A Recognition document of this deduction is still in Done status
Solution: Cancel every Done Recognition document of this deduction first
""" % (
                self._description,
                self.id,
            )
            raise UserError(_(error_message))

    @ssi_decorator.pre_open_action()
    def _05_check_reconcilable(self):
        """Reject opening a document that cannot be reconciled.

        Checks, per Allocation line, that its invoice's Receivable
        Account matches this document's own, that account allows
        reconciliation, that the invoice's Partner and Currency match
        this document's, and that its Amount Allocated does not
        exceed the invoice's own residual. Also requires this
        document's Amount Unallocated to be zero.

        :raises UserError: when any of the checks above fails.
        """
        self.ensure_one()
        for allocation in self.allocation_ids:
            invoice = allocation.customer_invoice_id
            if allocation.invoice_account_id != self.receivable_account_id:
                error_message = """
Document Type: %s
Context: Open deduction
Database ID: %s
Problem: Invoice '%s' Receivable Account does not match this document's own
Solution: Select an invoice whose Receivable Account matches this document's own
""" % (
                    self._description,
                    self.id,
                    invoice.display_name,
                )
                raise UserError(_(error_message))
            if not allocation.invoice_account_id.reconcile:
                error_message = """
Document Type: %s
Context: Open deduction
Database ID: %s
Problem: Receivable Account '%s' does not allow reconciliation
Solution: Enable reconciliation on the Receivable Account
""" % (
                    self._description,
                    self.id,
                    allocation.invoice_account_id.display_name,
                )
                raise UserError(_(error_message))
            if invoice.partner_id != self.partner_id:
                error_message = """
Document Type: %s
Context: Open deduction
Database ID: %s
Problem: Invoice '%s' Partner does not match this document's Partner
Solution: Select an invoice billed to this document's Partner
""" % (
                    self._description,
                    self.id,
                    invoice.display_name,
                )
                raise UserError(_(error_message))
            if invoice.currency_id != self.currency_id:
                error_message = """
Document Type: %s
Context: Open deduction
Database ID: %s
Problem: Invoice '%s' Currency does not match this document's Currency
Solution: Select an invoice in this document's Currency
""" % (
                    self._description,
                    self.id,
                    invoice.display_name,
                )
                raise UserError(_(error_message))
            if allocation.amount_allocated > allocation.invoice_residual:
                error_message = """
Document Type: %s
Context: Open deduction
Database ID: %s
Problem: Amount Allocated %s on invoice '%s' exceeds its residual %s
Solution: Lower the Amount Allocated to the invoice's own residual
""" % (
                    self._description,
                    self.id,
                    allocation.amount_allocated,
                    invoice.display_name,
                    allocation.invoice_residual,
                )
                raise UserError(_(error_message))
        precision = self.company_currency_id.decimal_places
        if not float_is_zero(self.amount_unallocated, precision_digits=precision):
            error_message = """
Document Type: %s
Context: Open deduction
Database ID: %s
Problem: Amount Unallocated is %s instead of zero
Solution: Allocate the full Amount Total across the Allocation lines
""" % (
                self._description,
                self.id,
                self.amount_unallocated,
            )
            raise UserError(_(error_message))

    @ssi_decorator.post_open_action()
    def _10_create_accounting_entry(self):
        """Create and post this document's ``account.move``.

        Creates the header move, this document's own credit line to
        the Receivable Account (saved to
        ``receivable_move_line_id``), a debit line per Deduction
        Line, then posts the move.

        :return: nothing
        """
        self.ensure_one()
        self._create_standard_move()  # Mixin
        ml = self._create_standard_ml()  # Mixin
        self.write(
            {
                "receivable_move_line_id": ml.id,
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
    def _20_reconcile(self):
        """Reconcile the receivable line against every allocated invoice.

        Every allocation reaching this hook already cleared
        ``_05_check_reconcilable``, so ``lines`` below is never empty
        and ``reconcile()`` always has a genuine, unreconciled amount
        on both sides to match -- ``partials`` is therefore never
        empty in practice. The slice-and-``.id`` idiom below still
        degrades safely to ``False`` instead of an ``IndexError`` if
        that ever stops holding, without an explicit branch to guard
        it.

        :return: nothing; assigns ``partial_reconcile_id`` on each
            Allocation line
        """
        self.ensure_one()
        no_partial = self.env["account.partial.reconcile"]
        for allocation in self.allocation_ids:
            lines = self.receivable_move_line_id + allocation.invoice_move_line_id
            result = lines.reconcile()
            partial = result.get("partials", no_partial)[:1]
            allocation.write(
                {
                    "partial_reconcile_id": partial.id,
                }
            )

    @ssi_decorator.post_open_action()
    def _30_mark_schedule_realized(self):
        """Flip every realized Schedule line to state ``realized``.

        :return: nothing
        """
        self.ensure_one()
        schedules = self.line_ids.mapped("schedule_id")
        schedules.write(
            {
                "deduction_id": self.id,
                "state": "realized",
            }
        )

    @ssi_decorator.post_cancel_action()
    def _10_unreconcile(self):
        """Undo the reconciliation created by ``_20_reconcile``.

        Must run before ``_20_delete_accounting_entry``: the journal
        entry cannot be deleted while its lines are still
        reconciled.

        :return: nothing
        """
        self.ensure_one()
        if self.receivable_move_line_id:
            self.receivable_move_line_id.remove_move_reconcile()

    @ssi_decorator.post_cancel_action()
    def _20_delete_accounting_entry(self):
        """Delete this document's ``account.move``.

        :return: nothing
        """
        self.ensure_one()
        self._delete_standard_move()  # Mixin

    @ssi_decorator.post_cancel_action()
    def _30_reset_schedule(self):
        """Reset every realized Schedule line back to ``scheduled``.

        :return: nothing
        """
        self.ensure_one()
        self.schedule_ids.write(
            {
                "deduction_id": False,
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
