# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare, float_round

from odoo.addons.ssi_decorator import ssi_decorator


class SchoolScholarshipDeductionRecognition(models.Model):
    """
    Represents one release of a deferred scholarship deduction into
    its own Final Account.
    A deduction whose own ``recognition_method`` is ``deferred`` books
    each of its Lines to a temporary Deferred Account instead of that
    Line's own Final Account. This document later moves ``amount`` --
    once for the full ``amount_deferred``, or several times for
    amortization -- from the Deferred Account to each Line's own
    Final Account, proportionally to ``ratio`` (this document's
    ``amount`` divided by the deduction's own ``amount_total``), so
    every funding source's Analytic Account is still represented in
    the resulting journal entry. Opening this document never touches
    the deduction's own Receivable Account or its reconciliation --
    those were already settled when the deduction itself was opened;
    this document only reclassifies the deduction's own debit side.
    """

    _name = "school_scholarship_deduction_recognition"
    _inherit = [
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_confirm",
        "mixin.company_currency",
        "mixin.account_move",
    ]
    _description = "School Scholarship Deduction Recognition"
    _order = "date, id"

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "done"
    _approval_state = "confirm"
    _after_approved_method = "action_done"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True
    _automatically_insert_done_policy_fields = False
    _automatically_insert_done_button = False

    _statusbar_visible_label = "draft,confirm,done"
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
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_reject",
        "dom_done",
        "dom_cancel",
    ]

    # Sequence attribute
    _create_sequence_state = "done"

    # Accounting Entry Header Mixin (``mixin.account_move``)
    _journal_id_field_name = "journal_id"
    _move_id_field_name = "move_id"
    _accounting_date_field_name = "date"
    _currency_id_field_name = "currency_id"
    _company_currency_id_field_name = "company_currency_id"

    deduction_id = fields.Many2one(
        string="# Deduction",
        comodel_name="school_scholarship_deduction",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Deferred deduction document this document releases.",
    )
    date = fields.Date(
        string="Date",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Accounting date of this recognition document. May not "
        "be earlier than the deduction's own Date.",
    )
    amount = fields.Monetary(
        string="Amount",
        currency_field="currency_id",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Portion of the deduction's own Amount Deferred released "
        "by this document. The sum of every Done Recognition's "
        "Amount may not exceed the deduction's own Amount Total.",
    )
    ratio = fields.Float(
        string="Ratio",
        compute="_compute_ratio",
        help="This document's own Amount divided by the deduction's "
        "own Amount Total -- the proportion of each Line released "
        "by this document.",
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
        help="Accounting journal this document's own entry posts to.",
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
    move_id = fields.Many2one(
        string="Move",
        comodel_name="account.move",
        readonly=True,
        copy=False,
        help="Journal entry generated when this document is Done.",
    )
    recognition_line_ids = fields.One2many(
        string="Recognition Lines",
        comodel_name="school_scholarship_deduction_recognition_line",
        inverse_name="recognition_id",
        readonly=True,
        copy=False,
        help="One technical line per deduction Line, each carrying "
        "the debit/credit pair posted for it. Generated when this "
        "document is Done; cleared again if it is cancelled.",
    )
    note = fields.Text(
        string="Note",
        help="Free-form note about this recognition document.",
    )

    @api.depends("amount", "deduction_id.amount_total")
    def _compute_ratio(self):
        """Compute the proportion of the deduction released by this document.

        :return: nothing; assigns ``ratio``
        """
        for record in self:
            ratio = 0.0
            if record.deduction_id.amount_total:
                ratio = record.amount / record.deduction_id.amount_total
            record.ratio = ratio

    @api.onchange("deduction_id")
    def onchange_amount(self):
        """Default Amount from the deduction's own Amount Deferred.

        :return: nothing
        """
        self.amount = 0.0
        if self.deduction_id:
            self.amount = self.deduction_id.amount_deferred

    @api.onchange("deduction_id")
    def onchange_journal_id(self):
        """Default Journal from the deduction's own Recognition Journal.

        :return: nothing
        """
        self.journal_id = False
        if self.deduction_id:
            self.journal_id = self.deduction_id.recognition_journal_id

    @api.constrains("amount", "date", "state")
    def _check_amount_not_exceed_deferred(self):
        """Forbid Done Recognitions of a deduction exceeding its total.

        :raises ValidationError: when the sum of every Done
            Recognition's Amount on the same deduction exceeds that
            deduction's own Amount Total.
        """
        for record in self:
            if record.state != "done":
                continue
            deduction = record.deduction_id
            done_recognitions = deduction.recognition_ids.filtered(
                lambda recognition: recognition.state == "done"
            )
            total_recognized = sum(done_recognitions.mapped("amount"))
            precision = deduction.company_currency_id.decimal_places
            if (
                float_compare(
                    total_recognized,
                    deduction.amount_total,
                    precision_digits=precision,
                )
                > 0
            ):
                error_message = """
Document Type: %s
Context: Configure recognition amount
Database ID: %s
Problem: Total Done Recognition amount %s exceeds the deduction's own Amount Total %s
Solution: Lower this document's own Amount so the total stays within Amount Total
""" % (
                    record._description,
                    record.id,
                    total_recognized,
                    deduction.amount_total,
                )
                raise ValidationError(_(error_message))

    @api.constrains("date")
    def _check_date_not_before_deduction(self):
        """Forbid a Date earlier than the deduction's own Date.

        :raises ValidationError: when ``date`` is earlier than
            ``deduction_id.date``.
        """
        for record in self:
            if (
                record.date
                and record.deduction_id.date
                and (record.date < record.deduction_id.date)
            ):
                error_message = """
Document Type: %s
Context: Configure recognition date
Database ID: %s
Problem: Date %s is earlier than the deduction's own Date %s
Solution: Select a Date on or after the deduction's own Date
""" % (
                    record._description,
                    record.id,
                    record.date,
                    record.deduction_id.date,
                )
                raise ValidationError(_(error_message))

    @ssi_decorator.post_done_action()
    def _10_create_accounting_entry(self):
        """Create and post this document's ``account.move``.

        Creates the header move, one
        ``school_scholarship_deduction_recognition_line`` per Line of
        the deduction (rounded to the currency's own precision, with
        the rounding remainder charged to the last line so the move
        stays balanced), then posts the move.

        :return: nothing
        """
        self.ensure_one()
        self._create_standard_move()
        self._create_recognition_lines()
        for recognition_line in self.recognition_line_ids:
            recognition_line._create_standard_ml()
        self._post_standard_move()

    def _create_recognition_lines(self):
        """Create one Recognition Line per Line of the deduction.

        :return: the created
            ``school_scholarship_deduction_recognition_line``
            recordset
        """
        self.ensure_one()
        Line = self.env["school_scholarship_deduction_recognition_line"]
        deduction_lines = self.deduction_id.line_ids
        if not deduction_lines:
            return Line
        precision = self.company_currency_id.decimal_places
        amounts = [
            float_round(
                deduction_line.price_subtotal * self.ratio,
                precision_digits=precision,
            )
            for deduction_line in deduction_lines
        ]
        remainder = float_round(self.amount - sum(amounts), precision_digits=precision)
        amounts[-1] = float_round(amounts[-1] + remainder, precision_digits=precision)
        lines = Line
        for deduction_line, amount in zip(deduction_lines, amounts):
            lines |= Line.create(self._prepare_recognition_line(deduction_line, amount))
        return lines

    def _prepare_recognition_line(self, deduction_line, amount):
        """Build one Recognition Line's create values.

        :param deduction_line: the ``school_scholarship_deduction_line``
            this Recognition Line releases
        :param amount: this Recognition Line's own share of
            ``amount``, already rounded
        :return: dict of
            ``school_scholarship_deduction_recognition_line`` values
        """
        self.ensure_one()
        return {
            "recognition_id": self.id,
            "deduction_line_id": deduction_line.id,
            "amount": amount,
        }

    @ssi_decorator.post_cancel_action()
    def _10_delete_accounting_entry(self):
        """Delete this document's ``account.move``.

        :return: nothing
        """
        self.ensure_one()
        self._delete_standard_move()

    @ssi_decorator.post_cancel_action()
    def _20_delete_recognition_lines(self):
        """Delete this document's own Recognition Lines.

        Regenerated from scratch by ``_create_recognition_lines`` the
        next time this document reaches Done.

        :return: nothing
        """
        self.ensure_one()
        self.recognition_line_ids.unlink()

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

        :return: the base policy fields of the standard three-mixin
            workflow combo
        """
        res = super()._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "done_ok",
            "cancel_ok",
            "reject_ok",
            "restart_ok",
            "restart_approval_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res
