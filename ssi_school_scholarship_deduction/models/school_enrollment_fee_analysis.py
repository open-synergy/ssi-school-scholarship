# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SchoolEnrollmentFeeAnalysis(models.Model):
    """
    Adds the scholarship/cash split to the fee analysis SQL view.

    Wraps ``ssi_school``'s own query as a subquery and left-joins
    ``customer_invoice`` on ``customer_invoice_id`` to expose, per
    fee line, how much of its invoice's Realized Amount was covered
    by a scholarship deduction versus an actual cash deposit --
    letting pivot reports built on this view stop overstating cash
    receipts on invoices partly or fully settled by scholarship.
    """

    _name = "school_enrollment_fee_analysis"
    _inherit = [
        "school_enrollment_fee_analysis",
    ]

    amount_scholarship = fields.Monetary(
        string="Scholarship",
        currency_field="currency_id",
        readonly=True,
        help=(
            "Portion of the linked invoice's Realized Amount "
            "settled by a scholarship deduction. Zero when the fee "
            "line has no linked invoice yet."
        ),
    )
    amount_gross = fields.Monetary(
        string="Gross Realized",
        currency_field="currency_id",
        readonly=True,
        help=(
            "Realized Amount of the linked invoice, before splitting "
            "off the scholarship-settled portion. Equal to "
            "``amount_scholarship`` plus ``amount_net``."
        ),
    )
    amount_net = fields.Monetary(
        string="Net Cash",
        currency_field="currency_id",
        readonly=True,
        help=(
            "Realized Amount of the linked invoice net of the "
            "scholarship-settled portion -- the figure fee analysis "
            "reports should use as actual cash received."
        ),
    )

    def _select_query(self):
        """Left-join ``customer_invoice``'s scholarship split in.

        :return: the SQL ``SELECT`` statement backing this view,
            wrapping ``ssi_school``'s own query as a subquery
        """
        return """
            SELECT
                base.*,
                COALESCE(ci.amount_settled_by_scholarship, 0.0)
                    AS amount_scholarship,
                COALESCE(ci.amount_realized, 0.0) AS amount_gross,
                COALESCE(ci.amount_settled_by_cash, 0.0) AS amount_net
            FROM (%s) base
            LEFT JOIN customer_invoice ci
                ON ci.id = base.customer_invoice_id
        """ % (
            super()._select_query()
        )
