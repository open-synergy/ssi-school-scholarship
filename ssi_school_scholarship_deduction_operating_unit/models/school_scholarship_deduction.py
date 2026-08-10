# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError

from odoo.addons.ssi_decorator import ssi_decorator


class SchoolScholarshipDeduction(models.Model):
    """
    Extends School Scholarship Deduction with single operating unit
    support.

    Derives ``operating_unit_id`` from the selected Award's own
    Operating Unit (create-time and onchange), and propagates it to
    the ``account.move`` this document creates on ``action_open`` --
    both the header itself (``_prepare_standard_move``) and its own
    credit journal item (``_prepare_standard_ml``, from
    ``mixin.account_move_single_line``). A second guard,
    ``_10_check_allocation_operating_unit``, re-checks every
    Allocation line's own Operating Unit as a ``pre_open_action`` hook
    so a document whose ``school_scholarship_deduction_allocation``
    constrain was bypassed via context (see that model's own
    ``_check_operating_unit``) still cannot reach
    ``_10_create_accounting_entry`` and post a journal entry mixing
    two Operating Units.
    """

    _name = "school_scholarship_deduction"
    _inherit = [
        "school_scholarship_deduction",
        "mixin.single_operating_unit",
    ]

    @api.model
    def create(self, vals):
        """Derive ``operating_unit_id`` from the selected Award.

        Overridden so ``operating_unit_id`` always reflects the
        selected Award's own Operating Unit rather than the creating
        user's default operating unit from
        ``mixin.single_operating_unit``, unless the caller explicitly
        passes ``operating_unit_id`` in the same ``vals``.

        :param vals: values for the new record
        :return: the created ``school_scholarship_deduction`` record
        """
        self._derive_operating_unit_from_award(vals)
        return super().create(vals)

    def _derive_operating_unit_from_award(self, vals):
        """Mutate ``vals`` in place, deriving ``operating_unit_id``.

        Applies only when ``award_id`` is present in ``vals`` and the
        caller has not already supplied ``operating_unit_id``
        explicitly in the same ``vals`` -- an explicit value always
        wins.

        :param vals: the ``create`` values dict, mutated in place
        :return: None
        """
        if "award_id" not in vals or "operating_unit_id" in vals:
            return
        award = self.env["school_scholarship_award"].browse(vals["award_id"])
        if award.operating_unit_id:
            vals["operating_unit_id"] = award.operating_unit_id.id

    @api.onchange("award_id")
    def onchange_operating_unit_id(self):
        """Set ``operating_unit_id`` from the selected Award.

        Mirrors the ``create`` derivation so the form shows the
        correct Operating Unit as soon as an Award is selected.

        :return: nothing
        """
        self.operating_unit_id = False
        if self.award_id:
            self.operating_unit_id = self.award_id.operating_unit_id

    def _prepare_standard_move(self):
        """Add this document's Operating Unit to the ``account.move``.

        :return: dict of ``account.move`` values
        """
        res = super()._prepare_standard_move()
        res["operating_unit_id"] = self.operating_unit_id.id
        return res

    def _prepare_standard_ml(self):
        """Add this document's Operating Unit to its own credit line.

        This document's own ``account.move.line`` (the header's
        credit line to the Receivable Account, from
        ``mixin.account_move_single_line``) carries the same
        Operating Unit as the document itself.

        :return: dict of ``account.move.line`` values
        """
        res = super()._prepare_standard_ml()
        res["operating_unit_id"] = self.operating_unit_id.id
        return res

    @ssi_decorator.pre_open_action()
    def _10_check_allocation_operating_unit(self):
        """Reject opening when an Allocation targets a different OU.

        :raises UserError: when any Allocation line's own Customer
            Invoice belongs to a different Operating Unit than this
            document.
        """
        self.ensure_one()
        for allocation in self.allocation_ids:
            invoice_ou = allocation.customer_invoice_id.operating_unit_id
            if (
                invoice_ou
                and self.operating_unit_id
                and invoice_ou != self.operating_unit_id
            ):
                error_message = """
Document Type: %s
Context: Open deduction
Database ID: %s
Problem: Invoice '%s' belongs to a different Operating Unit than this document
Solution: Select an invoice from the same Operating Unit as this document
""" % (
                    self._description,
                    self.id,
                    allocation.customer_invoice_id.display_name,
                )
                raise UserError(_(error_message))
