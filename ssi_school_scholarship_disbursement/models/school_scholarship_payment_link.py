# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SchoolScholarshipPaymentLink(models.Model):
    """
    Represents one ``account.payment`` linked to a scholarship
    disbursement document.

    Unlike ``school_scholarship_deduction``, this module never
    creates nor reconciles the payment itself -- creating an
    ``account.payment`` is out of this item's scope (see the
    Keputusan Desain's "Tidak termasuk" note). A payment link row
    only records that a given payment settles (part of) this
    document's own Payable Move Line, once that payment and its
    reconciliation already exist.
    """

    _name = "school_scholarship_payment_link"
    _description = "School Scholarship Disbursement - Payment Link"
    _order = "disbursement_id, id"

    disbursement_id = fields.Many2one(
        string="# Disbursement",
        comodel_name="school_scholarship_disbursement",
        required=True,
        ondelete="cascade",
        help="Disbursement document this payment link belongs to.",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="disbursement_id.currency_id",
        help="Currency of the parent document.",
    )
    payment_id = fields.Many2one(
        string="Payment",
        comodel_name="account.payment",
        required=True,
        ondelete="restrict",
        help="Payment that settles (part of) this document's own "
        "Payable Account. Must already exist -- this document does "
        "not create it.",
    )
    amount = fields.Monetary(
        string="Amount",
        currency_field="currency_id",
        related="payment_id.amount",
        help="Amount of the linked payment.",
    )
    partial_reconcile_id = fields.Many2one(
        string="Partial Reconcile",
        comodel_name="account.partial.reconcile",
        readonly=True,
        copy=False,
        help="Reconciliation record linking the payment to this "
        "document's own Payable Move Line, once that reconciliation "
        "has been made outside this document.",
    )
