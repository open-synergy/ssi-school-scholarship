# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SchoolScholarshipType(models.Model):
    """
    Represents a category of scholarship a school can grant to a student.
    Holds the full set of default accounting configuration (journals and
    accounts) a scholarship of this type posts to, so that every
    scholarship document created from it books its discount, expense, or
    payable entries consistently without the user re-selecting accounts
    on each document.
    """

    _name = "school_scholarship_type"
    _inherit = ["mixin.master_data"]
    _description = "School Scholarship Type"
    _order = "sequence, id"

    sequence = fields.Integer(
        string="Sequence",
        default=5,
        required=True,
        help="Display order of the scholarship type. Lower values appear "
        "first in the list.",
    )
    deduction_journal_id = fields.Many2one(
        string="Deduction Journal",
        comodel_name="account.journal",
        required=True,
        ondelete="restrict",
        help="Journal used to post the scholarship deduction (discount) "
        "entry on the student invoice. Must not be a Cash or Bank "
        "journal — a deduction never involves an actual cash movement.",
    )
    discount_account_id = fields.Many2one(
        string="Discount Account",
        comodel_name="account.account",
        required=True,
        ondelete="restrict",
        help="Contra-revenue account the scholarship deduction is booked "
        "to. Must not be a reconcilable account.",
    )
    employee_benefit_account_id = fields.Many2one(
        string="Employee Benefit Account",
        comodel_name="account.account",
        ondelete="restrict",
        help="Employee benefit expense account used instead of the "
        "Discount Account when this scholarship type is flagged as an "
        "employee benefit.",
    )
    is_employee_benefit = fields.Boolean(
        string="Is Employee Benefit",
        default=False,
        help="Check this if the scholarship under this type is granted as "
        "an employee benefit (e.g. tuition fee relief for staff "
        "children), so it is booked to the Employee Benefit Account "
        "instead of the Discount Account.",
    )
    disbursement_journal_id = fields.Many2one(
        string="Disbursement Journal",
        comodel_name="account.journal",
        ondelete="restrict",
        help="Journal used to post the cash disbursement entry when the "
        "scholarship is paid out to the student instead of deducted "
        "from the invoice.",
    )
    expense_account_id = fields.Many2one(
        string="Expense Account",
        comodel_name="account.account",
        ondelete="restrict",
        help="Expense account the cash scholarship disbursement is booked " "to.",
    )
    payable_account_id = fields.Many2one(
        string="Payable Account",
        comodel_name="account.account",
        ondelete="restrict",
        help="Payable account used to record the school's obligation to "
        "the student before the cash scholarship is disbursed. Must be "
        "a reconcilable account so the disbursement can be settled "
        "against it.",
    )
    deferred_discount_account_id = fields.Many2one(
        string="Deferred Discount Account",
        comodel_name="account.account",
        ondelete="restrict",
        help="Asset account used to defer recognition of the scholarship "
        "deduction across periods, before it is recognised to the "
        "Discount Account.",
    )
    deferred_expense_account_id = fields.Many2one(
        string="Deferred Expense Account",
        comodel_name="account.account",
        ondelete="restrict",
        help="Asset account used to defer recognition of the cash "
        "scholarship expense across periods, before it is recognised "
        "to the Expense Account.",
    )
    recognition_journal_id = fields.Many2one(
        string="Recognition Journal",
        comodel_name="account.journal",
        ondelete="restrict",
        help="Journal used to post the periodic recognition entry that "
        "releases the deferred discount or deferred expense.",
    )
    deduction_product_id = fields.Many2one(
        string="Deduction Product",
        comodel_name="product.product",
        ondelete="restrict",
        help="Product used to mark the scholarship deduction line on the "
        "student invoice.",
    )

    @api.constrains("discount_account_id")
    def _check_discount_account_id(self):
        """Forbid a reconcilable Discount Account.

        The Discount Account is a nominal contra-revenue account, not
        an open-item account settled against payments — allowing
        ``reconcile = True`` would let it be used as a counterpart
        account by mistake.

        :raises UserError: when ``discount_account_id.reconcile`` is
            ``True``.
        """
        for record in self:
            if record.discount_account_id and record.discount_account_id.reconcile:
                error_message = """
Document Type: %s
Context: Configure discount account
Database ID: %s
Problem: Discount Account is set as a reconcilable account
Solution: Select a non-reconcilable account, or disable Allow
Reconciliation on the selected account
""" % (
                    self._description,
                    record.id,
                )
                raise UserError(_(error_message))

    @api.constrains("payable_account_id")
    def _check_payable_account_id(self):
        """Require a reconcilable Payable Account when it is set.

        The Payable Account tracks the school's obligation to the
        student until the cash scholarship is disbursed; without
        ``reconcile = True`` the disbursement entry could never be
        settled against it.

        :raises UserError: when ``payable_account_id`` is set and its
            ``reconcile`` is ``False``.
        """
        for record in self:
            if record.payable_account_id and not record.payable_account_id.reconcile:
                error_message = """
Document Type: %s
Context: Configure payable account
Database ID: %s
Problem: Payable Account is not set as a reconcilable account
Solution: Enable Allow Reconciliation on the selected account
""" % (
                    self._description,
                    record.id,
                )
                raise UserError(_(error_message))

    @api.constrains(
        "deferred_discount_account_id",
        "deferred_expense_account_id",
    )
    def _check_deferred_account_type(self):
        """Require the deferred accounts to be of the Asset type.

        Both the Deferred Discount Account and Deferred Expense Account
        hold amounts not yet recognised, so they must belong to an
        account type whose ``internal_group`` is ``asset``.

        :raises UserError: when either deferred account is set and its
            ``user_type_id.internal_group`` is not ``asset``.
        """
        for record in self:
            for field_name, label in (
                ("deferred_discount_account_id", "Deferred Discount"),
                ("deferred_expense_account_id", "Deferred Expense"),
            ):
                account = record[field_name]
                if account and account.user_type_id.internal_group != "asset":
                    error_message = """
Document Type: %s
Context: Configure %s Account
Database ID: %s
Problem: %s Account is not an asset-type account
Solution: Select an account whose Type belongs to the Asset group
""" % (
                        self._description,
                        label,
                        record.id,
                        label,
                    )
                    raise UserError(_(error_message))

    @api.constrains("deduction_journal_id")
    def _check_deduction_journal_id(self):
        """Forbid a Cash or Bank journal as the Deduction Journal.

        A deduction is a contra-revenue entry on the invoice, not an
        actual money movement — posting it through a Cash or Bank
        journal would wrongly imply cash was received.

        :raises UserError: when ``deduction_journal_id.type`` is
            ``cash`` or ``bank``.
        """
        for record in self:
            if record.deduction_journal_id.type in ("bank", "cash"):
                error_message = """
Document Type: %s
Context: Configure deduction journal
Database ID: %s
Problem: Deduction Journal is a Cash or Bank journal
Solution: Select a journal that is not of type Cash or Bank
""" % (
                    self._description,
                    record.id,
                )
                raise UserError(_(error_message))
