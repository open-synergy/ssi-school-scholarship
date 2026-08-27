# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class SchoolScholarshipFundingSource(models.Model):
    """
    Extends School Scholarship Funding Source to draw its commitment
    and realization from a ``donation_fund``, through
    ``mixin.donation_fund_consumer``.

    A Funding Source is master data with no state field of its own,
    so ``_donation_state_field_name`` is set to ``False``.
    ``mixin.donation_fund_consumer._prepare_donation_fund_usage``
    then reads a consumer's state as ``False`` whenever
    ``_donation_state_field_name`` is falsy, so
    ``_donation_committed_states`` must contain that exact ``False``
    sentinel -- ``(False,)``, not an empty tuple and not the mixin's
    own default ``("open", "done")`` -- for
    ``amount_committed`` to ever be counted onto the ledger. Getting
    this tuple wrong leaves the ledger permanently at zero, with no
    error to say why.

    ``amount_committed``/``amount_realized`` are ``compute`` +
    ``store=True`` fields. In Odoo 14, ``Model.flush()`` recomputes
    stored compute fields by calling ``_write()`` directly
    (``odoo/models.py``), never ``write()`` -- so the mixin's own
    ``write()`` override never observes those recomputations by
    itself. ``_write()`` is overridden here for that reason alone.

    That refresh is deliberately update-only, never creating a
    ledger row. ``mixin.donation_fund_consumer.
    _donation_fund_usage_refresh`` reads a stored compute field
    through ``_prepare_donation_fund_usage``, which can itself
    trigger a flush -- and therefore a *nested* call into
    ``_write()`` -- before the outer refresh's own ``search()``
    result is used to decide between ``create``/``write``. That
    interleaving lets the outer call insert a second
    ``donation_fund_usage`` row for the same ``(model_id, res_id)``
    once the nested call has already inserted the first one,
    violating the table's unique constraint. Restricting this
    hook to updating a row that already exists is safe under any
    interleaving: creation and deletion of a ledger row stay
    entirely the mixin's own ``create()``/``write()``/``unlink()``
    responsibility.
    """

    _name = "school_scholarship_funding_source"
    _inherit = [
        "school_scholarship_funding_source",
        "mixin.donation_fund_consumer",
    ]

    _donation_committed_field_name = "amount_committed"
    _donation_realized_field_name = "amount_realized"
    _donation_state_field_name = False
    _donation_committed_states = (False,)

    def _write(self, vals):
        """Write raw column values, then update an EXISTING ledger row.

        Overridden instead of ``write()`` because Odoo 14's
        ``Model.flush()`` recomputes stored compute fields (such as
        ``amount_committed``/``amount_realized``) by calling
        ``_write()`` directly, bypassing ``write()`` entirely --
        this is the only hook that observes those recomputed values.
        Update-only by design -- see the class docstring for why
        this must never create or delete a ledger row.

        :param vals: raw column values being written
        :return: True, as returned by the base ``_write``
        """
        result = super()._write(vals)
        relevant_fields = self._donation_fund_usage_relevant_fields()
        if any(field_name in vals for field_name in relevant_fields):
            self.sudo()._donation_fund_usage_update_only()
        return result

    def _donation_fund_usage_update_only(self):
        """Update this record's ``donation_fund_usage`` row, if any.

        Unlike ``mixin.donation_fund_consumer.
        _donation_fund_usage_refresh``, this never creates or
        deletes a ledger row -- only the mixin's own ``create()``,
        ``write()``, and ``unlink()`` do that. It exists solely so
        ``_write()`` can pick up committed/realized amounts
        recomputed by ``Model.flush()`` without risking a duplicate
        ``(model_id, res_id)`` row from a nested flush triggered by
        reading those very stored compute fields.

        :return: nothing
        """
        Usage = self.env["donation_fund_usage"].sudo()  # pylint: disable=invalid-name
        model = self._donation_fund_usage_model()
        for record in self:
            if not record.donation_fund_id:
                continue
            usage = Usage.search(
                [
                    ("model_id", "=", model.id),
                    ("res_id", "=", record.id),
                ],
                limit=1,
            )
            if not usage:
                continue
            usage.write(record._prepare_donation_fund_usage())

    @api.constrains("donation_fund_id", "analytic_account_id")
    def _check_donation_fund_analytic_account(self):
        """Forbid a Donation Fund bound to a different Analytic Account.

        The Analytic Account is the sole boundary both this model
        and ``donation_fund`` use to identify their own money, so a
        Funding Source may only draw from a Donation Fund bound to
        the very same Analytic Account it is itself bound to.

        :raises ValidationError: when ``donation_fund_id`` is set and
            its ``analytic_account_id`` differs from this record's
            own ``analytic_account_id``.
        """
        for record in self:
            if not record.donation_fund_id:
                continue
            if (
                record.donation_fund_id.analytic_account_id
                != record.analytic_account_id
            ):
                error_message = """
Document Type: %s
Context: Configure Donation Fund
Database ID: %s
Problem: Donation Fund's Analytic Account does not match this Funding
Source's Analytic Account
Solution: Select a Donation Fund bound to the same Analytic Account as
this Funding Source, or change this Funding Source's Analytic Account
to match
""" % (
                    self._description,
                    record.id,
                )
                raise ValidationError(_(error_message))
