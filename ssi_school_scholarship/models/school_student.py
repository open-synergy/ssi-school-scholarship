# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SchoolStudent(models.Model):
    """
    Adds scholarship visibility to the student card.
    Exposes the scholarship awards granted to a student together with
    two confidentiality-gated indicators -- whether the student
    currently holds a scholarship, and which award (if any) is in
    effect today -- so front office staff can tell a scholarship
    recipient apart from a regular student without opening the
    Scholarship app themselves.
    """

    _name = "school_student"
    _inherit = [
        "school_student",
    ]

    scholarship_award_ids = fields.One2many(
        string="Scholarship Awards",
        comodel_name="school_scholarship_award",
        inverse_name="student_id",
        help="Scholarship awards granted to this student.",
    )
    active_award_id = fields.Many2one(
        string="Active Scholarship Award",
        comodel_name="school_scholarship_award",
        compute="_compute_active_award_id",
        store=False,
        compute_sudo=True,
        groups="ssi_school_scholarship.school_scholarship_award_viewer_group",
        help=(
            "Open award whose period covers today, i.e. the "
            "scholarship currently in effect for this student. "
            "Restricted to the Scholarship Award Viewer group -- "
            "confidential, must not leak through export or reports."
        ),
    )
    has_scholarship = fields.Boolean(
        string="Has Scholarship",
        compute="_compute_has_scholarship",
        store=True,
        compute_sudo=True,
        groups="ssi_school_scholarship.school_scholarship_award_viewer_group",
        help=(
            "True when this student has at least one Open or Done "
            "scholarship award. Restricted to the Scholarship Award "
            "Viewer group -- must never be shown on the general "
            "student tree view or on class reports."
        ),
    )
    scholarship_award_count = fields.Integer(
        string="Scholarship Award Count",
        compute="_compute_scholarship_award_count",
        store=False,
        compute_sudo=True,
        help="Number of scholarship awards granted to this student.",
    )

    @api.depends(
        "scholarship_award_ids.state",
        "scholarship_award_ids.date_start",
        "scholarship_award_ids.date_end",
    )
    def _compute_active_award_id(self):
        """Resolve the Open award whose period covers today.

        Reads ``fields.Date.context_today`` at compute time, so the
        result moves with the calendar even when nothing on this
        record has changed -- the field is therefore ``store=False``
        despite declaring real field dependencies above. When more
        than one award qualifies, the one with the latest
        ``date_start`` wins.

        :return: nothing; assigns ``active_award_id``
        """
        today = fields.Date.context_today(self)
        for record in self:
            result = False
            candidates = record.scholarship_award_ids.filtered(
                lambda award: award.state == "open"
                and award.date_start
                and award.date_end
                and award.date_start <= today <= award.date_end
            )
            if candidates:
                result = candidates.sorted(
                    key=lambda award: award.date_start, reverse=True
                )[0]
            record.active_award_id = result

    @api.depends("scholarship_award_ids.state")
    def _compute_has_scholarship(self):
        """Flag students holding an Open or Done scholarship award.

        :return: nothing; assigns ``has_scholarship``
        """
        for record in self:
            result = False
            if record.scholarship_award_ids.filtered(
                lambda award: award.state in ("open", "done")
            ):
                result = True
            record.has_scholarship = result

    @api.depends("scholarship_award_ids")
    def _compute_scholarship_award_count(self):
        """Count the scholarship awards granted to this student.

        :return: nothing; assigns ``scholarship_award_count``
        """
        for record in self:
            record.scholarship_award_count = len(record.scholarship_award_ids)

    def action_open_scholarship_award(self):
        """Open the list of scholarship awards granted to this student.

        :return: an ``ir.actions.act_window`` dict
        """
        for record in self.sudo():
            result = record._open_scholarship_award()
        return result

    def _open_scholarship_award(self):
        """Build the window action listing this student's awards.

        :return: an ``ir.actions.act_window`` dict limited to the
            scholarship awards of this student
        """
        self.ensure_one()
        waction = self.env.ref(
            "ssi_school_scholarship.school_scholarship_award_action"
        ).read()[0]
        waction.update(
            {
                "domain": [("student_id", "=", self.id)],
                "context": {"default_student_id": self.id},
            }
        )
        return waction
