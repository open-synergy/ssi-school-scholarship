# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SchoolScholarshipAwardSchedule(models.Model):
    """
    Extends the award realization schedule with a link back to the
    disbursement document that realizes it.

    ``disbursement_id`` is the inverse of
    ``school_scholarship_disbursement``'s own ``schedule_ids``: a
    schedule line is linked here once a disbursement line targets it,
    and the link is what
    ``_20_mark_schedule_realized``/``_20_reset_schedule`` use to flip
    this line's ``state`` between ``scheduled`` and ``realized`` as
    the disbursement document opens or is cancelled.
    """

    _inherit = "school_scholarship_award_schedule"

    disbursement_id = fields.Many2one(
        string="# Disbursement",
        comodel_name="school_scholarship_disbursement",
        readonly=True,
        copy=False,
        help="Disbursement document that realizes this schedule line. "
        "Filled automatically once a disbursement line targets this "
        "schedule line and its document is opened; cleared again if "
        "that document is cancelled.",
    )
