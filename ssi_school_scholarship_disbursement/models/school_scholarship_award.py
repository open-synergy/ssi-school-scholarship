# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SchoolScholarshipAward(models.Model):
    """
    Extends the scholarship award with the ability to realize its own
    due Cash Schedule lines into Disbursement documents.

    ``_get_due_cash_schedule`` finds the Cash Schedule lines that are
    safe to realize: still ``scheduled`` and belonging to a Cash
    Benefit line -- a Cash Schedule line never carries a Payment Term
    (``school_scholarship_award_schedule._check_payment_term_required``),
    so, unlike the Fee Reduction deduction flow, there is no invoice
    to wait for. ``_create_due_disbursement`` then builds one draft
    ``school_scholarship_disbursement`` per Award, covering every due
    Cash Schedule line across every Funding line. Both methods are
    exercised from the ``create_due_scholarship_disbursement`` wizard,
    opened via ``action_open_create_due_disbursement_wizard``.
    """

    _name = "school_scholarship_award"
    _inherit = "school_scholarship_award"

    def action_open_create_due_disbursement_wizard(self):
        """Open the wizard that realizes due Cash Schedule lines.

        Available both from a single Award's form and from several
        Awards selected in the Scholarship Awards list view.

        :return: an ``ir.actions.act_window`` dict opening
            ``create_due_scholarship_disbursement``, with every
            selected Award pre-filled in its ``award_ids``
        """
        return self._open_create_due_disbursement_wizard()

    def _open_create_due_disbursement_wizard(self):
        """Build the window action opening the due disbursement wizard.

        Deliberately operates on the whole ``self`` recordset instead
        of a single record: the wizard's own ``award_ids`` must be
        pre-filled with every Award selected in the list view, not
        just one.

        :return: an ``ir.actions.act_window`` dict targeting ``new``,
            with every id in this recordset passed through
            ``active_ids``
        """
        waction = self.env.ref(
            "ssi_school_scholarship_disbursement."
            "create_due_scholarship_disbursement_action"
        ).read()[0]
        waction.update(
            {
                "context": {
                    "active_model": "school_scholarship_award",
                    "active_ids": self.ids,
                },
            }
        )
        return waction

    def _get_due_cash_schedule(self, date_start=False, date_end=False):
        """Filter this Award's due, unrealized Cash Schedule lines.

        A Cash Schedule line is due once it is still ``scheduled`` and
        its own Benefit line's ``benefit_type`` is ``cash`` -- unlike
        a Fee Reduction line, it never carries a Payment Term, so no
        invoice gate applies. A line already realized never matches
        (its own ``state`` is no longer ``scheduled``), which is what
        makes running this twice after the first Disbursement opens
        idempotent.

        :param date_start: earliest Schedule Date to include, or
            ``False`` for no lower bound
        :param date_end: latest Schedule Date to include, or
            ``False`` for no upper bound
        :return: the ``school_scholarship_award_schedule`` recordset
            matching every condition above
        """
        self.ensure_one()
        return self.schedule_ids.filtered(
            lambda schedule: schedule.state == "scheduled"
            and schedule.benefit_id.benefit_type == "cash"
            and (not date_start or schedule.date >= date_start)
            and (not date_end or schedule.date <= date_end)
        )

    def _create_due_disbursement(self, date_start=False, date_end=False):
        """Realize this Award's due Cash Schedule lines into a Disbursement.

        Groups every due Cash Schedule line returned by
        ``_get_due_cash_schedule`` -- across every Funding line -- into
        a single draft ``school_scholarship_disbursement`` document.
        Skips silently -- returning an empty recordset -- when this
        Award has no due Cash Schedule line at all, so a mass run from
        the wizard is never aborted by one uncooperative Award.

        :param date_start: earliest Schedule Date to include, or
            ``False`` for no lower bound
        :param date_end: latest Schedule Date to include, or
            ``False`` for no upper bound
        :return: the ``school_scholarship_disbursement`` recordset
            created by this call (possibly empty)
        """
        self.ensure_one()
        disbursements = self.env["school_scholarship_disbursement"]
        schedules = self._get_due_cash_schedule(date_start, date_end)
        if not schedules:
            return disbursements
        disbursements |= self.env["school_scholarship_disbursement"].create(
            self._prepare_due_disbursement_data(schedules)
        )
        return disbursements

    def _prepare_due_disbursement_data(self, schedules):
        """Build the ``school_scholarship_disbursement`` header values.

        Extension point: override to carry extra header fields into
        a newly created document.

        :param schedules: the due ``school_scholarship_award_schedule``
            recordset this document realizes
        :return: dict of ``school_scholarship_disbursement`` values,
            including the nested ``line_ids`` commands
        """
        self.ensure_one()
        today = fields.Date.context_today(self)
        line_values = []
        for schedule in schedules:
            for funding in self.funding_ids:
                line_values.append(
                    (
                        0,
                        0,
                        self._prepare_due_disbursement_line_data(schedule, funding),
                    )
                )
        return {
            "award_id": self.id,
            "date": today,
            "date_due": today,
            "journal_id": self.disbursement_journal_id.id,
            "payable_account_id": self.payable_account_id.id,
            "line_ids": line_values,
        }

    def _prepare_due_disbursement_line_data(self, schedule, funding):
        """Build one Disbursement Line's values for a (Schedule, Funding) pair.

        Mirrors ``school_scholarship_disbursement_line``'s own onchange
        handlers (``onchange_name``, ``onchange_product_id``,
        ``onchange_final_account_id``, ``onchange_price_unit``), which
        never fire on a plain ``create()`` call.

        :param schedule: the due ``school_scholarship_award_schedule``
            line being realized
        :param funding: this Award's own
            ``school_scholarship_award_funding`` line the amount is
            drawn from
        :return: dict of ``school_scholarship_disbursement_line``
            values
        """
        self.ensure_one()
        benefit = schedule.benefit_id
        return {
            "schedule_id": schedule.id,
            "funding_id": funding.id,
            "name": benefit.name,
            "product_id": benefit.product_id.id,
            "final_account_id": benefit.account_id.id,
            "uom_quantity": 1,
            "price_unit": schedule.amount_planned * funding.percentage / 100.0,
        }
