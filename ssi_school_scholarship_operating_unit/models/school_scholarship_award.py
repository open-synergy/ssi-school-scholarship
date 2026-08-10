# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models

from odoo.addons.ssi_school_operating_unit.models.school_enrollment_operating_unit_mixin import (  # noqa: B950 pylint: disable=line-too-long
    get_operating_unit_id_from_school,
)


class SchoolScholarshipAward(models.Model):
    """Extend School Scholarship Award with single operating unit support.

    Restricts each award record to one operating unit, and derives
    ``operating_unit_id`` from the school of the selected
    ``enrollment_id`` on create/write instead of relying solely on the
    creating user's default operating unit.

    Unlike ``school_enrollment`` in ``ssi_school_operating_unit`` --
    whose ``school_id`` is a plain, directly-settable field -- this
    model's ``school_id`` is a ``related``/``store`` field mirroring
    ``enrollment_id.school_id`` and is never present in ``create``/
    ``write`` ``vals``. Derivation is therefore keyed off
    ``enrollment_id`` instead, reusing the same
    ``get_operating_unit_id_from_school`` helper the existing adaptor
    provides so the "exactly one operating unit" rule itself is never
    duplicated.
    """

    _name = "school_scholarship_award"
    _inherit = [
        "school_scholarship_award",
        "mixin.single_operating_unit",
    ]

    @api.model
    def create(self, vals):
        """Derive ``operating_unit_id`` from the enrollment's school.

        Overridden so ``operating_unit_id`` always reflects the
        selected enrollment's school's own operating unit rather than
        the creating user's default operating unit from
        ``mixin.single_operating_unit``, unless the caller explicitly
        passes ``operating_unit_id`` in the same ``vals``.

        :param vals: values for the new record
        :return: the created ``school_scholarship_award`` record
        """
        self._derive_operating_unit_from_enrollment(vals)
        return super().create(vals)

    def write(self, vals):
        """Re-derive ``operating_unit_id`` when ``enrollment_id`` changes.

        Only triggers when ``enrollment_id`` is part of ``vals``, so a
        write that only sets ``operating_unit_id`` passes through
        unchanged.

        :param vals: values to write
        :return: True
        """
        self._derive_operating_unit_from_enrollment(vals)
        return super().write(vals)

    def _derive_operating_unit_from_enrollment(self, vals):
        """Mutate ``vals`` in place, deriving ``operating_unit_id``.

        Applies only when ``enrollment_id`` is present in ``vals`` and
        the caller has not already supplied ``operating_unit_id``
        explicitly in the same ``vals`` -- an explicit value always
        wins. The actual "exactly one operating unit" determination is
        delegated to ``get_operating_unit_id_from_school``, not
        reimplemented here.

        :param vals: the ``create``/``write`` values dict, mutated in
            place
        :return: None
        """
        if "enrollment_id" not in vals or "operating_unit_id" in vals:
            return
        enrollment = self.env["school_enrollment"].browse(vals["enrollment_id"])
        operating_unit_id = get_operating_unit_id_from_school(
            self.env, enrollment.school_id.id
        )
        if operating_unit_id:
            vals["operating_unit_id"] = operating_unit_id

    @api.onchange("school_id")
    def onchange_operating_unit_id(self):
        """Set ``operating_unit_id`` from the enrollment's school.

        Mirrors the ``create``/``write`` derivation so the form shows
        the correct operating unit as soon as an Enrollment is
        selected (``school_id`` is related to
        ``enrollment_id.school_id``, so this onchange fires in the
        same request as the Enrollment onchange). Only sets a value
        when the school has exactly one operating unit; otherwise the
        current value is left untouched.
        """
        if self.school_id and len(self.school_id.operating_unit_ids) == 1:
            self.operating_unit_id = self.school_id.operating_unit_ids
