# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models

from odoo.addons.ssi_school_operating_unit.models.school_enrollment_operating_unit_mixin import (  # noqa: B950 pylint: disable=line-too-long
    get_operating_unit_id_from_school,
)


class SchoolScholarshipAward(models.Model):
    """Extend School Scholarship Award to derive Operating Unit from
    an Admission billing source too.

    ``ssi_school_scholarship_operating_unit`` only derives
    ``operating_unit_id`` from ``enrollment_id`` (via
    ``_derive_operating_unit_from_enrollment``), so an award billed
    against an Admission (``source_type == "admission"``, added by
    ``ssi_school_scholarship_admission``) never carries
    ``enrollment_id`` in its ``create``/``write`` ``vals`` and falls
    back to the creating user's default operating unit from
    ``mixin.single_operating_unit`` instead of the Admission's own
    school's operating unit. This module adds the missing Admission
    branch, reusing the same ``get_operating_unit_id_from_school``
    helper the existing adaptors provide so the "exactly one operating
    unit" rule itself is never duplicated.
    """

    _name = "school_scholarship_award"
    _inherit = [
        "school_scholarship_award",
    ]

    @api.model
    def create(self, vals):
        """Derive ``operating_unit_id`` from the admission's school.

        Overridden so an Admission-sourced award's
        ``operating_unit_id`` always reflects the selected admission's
        school's own operating unit rather than the creating user's
        default operating unit, unless the caller explicitly passes
        ``operating_unit_id`` in the same ``vals``.

        :param vals: values for the new record
        :return: the created ``school_scholarship_award`` record
        """
        self._derive_operating_unit_from_admission(vals)
        return super().create(vals)

    def write(self, vals):
        """Re-derive ``operating_unit_id`` when ``admission_id`` changes.

        Only triggers when ``admission_id`` is part of ``vals``, so a
        write that only sets ``operating_unit_id`` passes through
        unchanged.

        :param vals: values to write
        :return: True
        """
        self._derive_operating_unit_from_admission(vals)
        return super().write(vals)

    def _derive_operating_unit_from_admission(self, vals):
        """Mutate ``vals`` in place, deriving ``operating_unit_id``.

        Applies only when ``admission_id`` is present in ``vals`` and
        the caller has not already supplied ``operating_unit_id``
        explicitly in the same ``vals`` -- an explicit value always
        wins. The actual "exactly one operating unit" determination is
        delegated to ``get_operating_unit_id_from_school``, not
        reimplemented here.

        :param vals: the ``create``/``write`` values dict, mutated in
            place
        :return: None
        """
        if "admission_id" not in vals or "operating_unit_id" in vals:
            return
        admission = self.env["school_admission"].browse(vals["admission_id"])
        operating_unit_id = get_operating_unit_id_from_school(
            self.env, admission.school_id.id
        )
        if operating_unit_id:
            vals["operating_unit_id"] = operating_unit_id
