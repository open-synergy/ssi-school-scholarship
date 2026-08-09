# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class SchoolScholarshipAward(models.Model):
    """
    Extends the scholarship award with the ability to realize its own
    due Schedule lines into Deduction documents.

    ``_get_due_schedule`` finds the Schedule lines that are safe to
    realize -- their own Payment Term must already be invoiced, and
    that invoice must be open, which together make it impossible for
    a Deduction to be created ahead of its own invoice.
    ``_create_due_deduction`` then groups those lines by invoice and
    creates one draft ``school_scholarship_deduction`` per group. Both
    methods are exercised from the ``create_due_scholarship_deduction``
    wizard, opened via ``action_open_create_due_deduction_wizard``.
    """

    _name = "school_scholarship_award"
    _inherit = "school_scholarship_award"

    def action_open_create_due_deduction_wizard(self):
        """Open the wizard that realizes due Schedule lines.

        Available both from a single Award's form and from several
        Awards selected in the Scholarship Awards list view; every
        selected Award must pass the ``create_deduction_ok`` policy
        check before the wizard opens.

        :return: an ``ir.actions.act_window`` dict opening
            ``create_due_scholarship_deduction``, with every selected
            Award pre-filled in its ``award_ids``
        """
        for record in self.sudo():
            record._check_create_deduction_policy()
        return self._open_create_due_deduction_wizard()

    def _check_create_deduction_policy(self):
        """Reject opening the wizard when the policy check fails.

        Mirrors ``_check_generate_schedule_policy`` on this same
        model: ``create_deduction_ok`` is a ``mixin.policy`` field
        whose compute only depends on ``policy_template_id``, so it
        must be busted explicitly in case a stale value was cached
        before this Award reached Open.

        :raises UserError: when ``create_deduction_ok`` is falsy and
            the context does not bypass the policy check.
        """
        self.ensure_one()
        if self.env.context.get("bypass_policy_check", False):
            return True
        self.invalidate_cache(fnames=["create_deduction_ok"], ids=self.ids)
        if not self.create_deduction_ok:
            error_message = """
Document Type: %s
Context: Open create due deduction wizard
Database ID: %s
Problem: Document is not allowed to create deduction
Solution: Check create deduction policy prerequisite
""" % (
                self._description,
                self.id,
            )
            raise UserError(_(error_message))
        return True

    def _open_create_due_deduction_wizard(self):
        """Build the window action opening the due deduction wizard.

        Deliberately operates on the whole ``self`` recordset instead
        of a single record: the wizard's own ``award_ids`` must be
        pre-filled with every Award selected in the list view, not
        just one.

        :return: an ``ir.actions.act_window`` dict targeting ``new``,
            with every id in this recordset passed through
            ``active_ids``
        """
        waction = self.env.ref(
            "ssi_school_scholarship_deduction."
            "create_due_scholarship_deduction_action"
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

    def _get_due_schedule(self, date_start=False, date_end=False):
        """Filter this Award's due, invoiced, unrealized Schedule lines.

        A Schedule line is due once its own Payment Term has actually
        been invoiced (``invoiced``) and that invoice is open
        (``open``) -- together these two conditions make it
        impossible for a Deduction to be created ahead of its own
        invoice. A line already realized never matches (its own
        ``state`` is no longer ``scheduled``), which is what makes
        running this twice after the first Deduction opens idempotent.

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
            and schedule.payment_term_id.state == "invoiced"
            and schedule.payment_term_id.customer_invoice_id.state == "open"
            and (not date_start or schedule.date >= date_start)
            and (not date_end or schedule.date <= date_end)
        )

    def _create_due_deduction(self, date_start=False, date_end=False):
        """Realize this Award's due Schedule lines into Deductions.

        Groups the due Schedule lines returned by
        ``_get_due_schedule`` by their own linked invoice, then
        creates one draft ``school_scholarship_deduction`` document
        per group. Skips silently -- returning an empty recordset --
        when this Award has no due Schedule line at all, so a mass
        run from the wizard is never aborted by one uncooperative
        Award.

        :param date_start: earliest Schedule Date to include, or
            ``False`` for no lower bound
        :param date_end: latest Schedule Date to include, or
            ``False`` for no upper bound
        :return: the ``school_scholarship_deduction`` recordset
            created by this call (possibly empty)
        """
        self.ensure_one()
        deductions = self.env["school_scholarship_deduction"]
        schedules = self._get_due_schedule(date_start, date_end)
        invoices = schedules.mapped("customer_invoice_id")
        for invoice in invoices:
            group = schedules.filtered(
                lambda schedule, invoice=invoice: schedule.customer_invoice_id
                == invoice
            )
            deductions |= self._create_deduction_for_invoice(invoice, group)
        return deductions

    def _create_deduction_for_invoice(self, invoice, schedules):
        """Create one Deduction document realizing one invoice's group.

        The header is created first (with its Lines, one per
        (Schedule, Funding) pairing), then the single Allocation line
        is added once the header's own ``amount_total`` has already
        been computed, so ``amount_allocated`` can be set to it
        exactly.

        :param invoice: the ``customer_invoice`` every line of
            ``schedules`` is due against
        :param schedules: the due ``school_scholarship_award_schedule``
            recordset to realize, all sharing ``invoice`` as their own
            Payment Term's invoice
        :return: the newly created ``school_scholarship_deduction``
            record
        """
        self.ensure_one()
        deduction = self.env["school_scholarship_deduction"].create(
            self._prepare_due_deduction_data(invoice, schedules)
        )
        deduction.write(
            {
                "allocation_ids": [
                    (
                        0,
                        0,
                        self._prepare_due_deduction_allocation_data(deduction, invoice),
                    )
                ],
            }
        )
        return deduction

    def _prepare_due_deduction_data(self, invoice, schedules):
        """Build the ``school_scholarship_deduction`` header values.

        Extension point: override to carry extra header fields into
        a newly created document.

        :param invoice: the ``customer_invoice`` this document will
            eventually be allocated against
        :param schedules: the ``school_scholarship_award_schedule``
            recordset this document realizes
        :return: dict of ``school_scholarship_deduction`` values,
            including the nested ``line_ids`` commands
        """
        self.ensure_one()
        line_values = []
        for schedule in schedules:
            for funding in self.funding_ids:
                line_values.append(
                    (
                        0,
                        0,
                        self._prepare_due_deduction_line_data(schedule, funding),
                    )
                )
        return {
            "award_id": self.id,
            "journal_id": self.deduction_journal_id.id,
            "receivable_account_id": invoice.receivable_account_id.id,
            "line_ids": line_values,
        }

    def _prepare_due_deduction_line_data(self, schedule, funding):
        """Build one Deduction Line's values for a (Schedule, Funding) pair.

        Mirrors ``school_scholarship_deduction_line``'s own onchange
        handlers (``onchange_name``, ``onchange_product_id``,
        ``onchange_final_account_id``, ``onchange_price_unit``), which
        never fire on a plain ``create()`` call.

        :param schedule: the due ``school_scholarship_award_schedule``
            line being realized
        :param funding: this Award's own
            ``school_scholarship_award_funding`` line the amount is
            drawn from
        :return: dict of ``school_scholarship_deduction_line`` values
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

    def _prepare_due_deduction_allocation_data(self, deduction, invoice):
        """Build the single Allocation line's values for one Deduction.

        :param deduction: the just-created ``school_scholarship_deduction``
            record, its own ``amount_total`` already computed from
            ``line_ids``
        :param invoice: the ``customer_invoice`` this Allocation line
            targets
        :return: dict of ``school_scholarship_deduction_allocation``
            values
        """
        self.ensure_one()
        return {
            "customer_invoice_id": invoice.id,
            "amount_allocated": deduction.amount_total,
        }
