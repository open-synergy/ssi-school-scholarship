# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SchoolEnrollment(models.Model):
    """
    Adds scholarship visibility to the enrollment record.
    Exposes the committed scholarship amount and the awards linked to
    this enrollment so billing staff can see the discount that
    applies to it. This is a commitment figure only: it never touches
    ``school_enrollment_payment_term`` or its detail lines, which
    stay the source of the actual billed/realized amounts -- keeping
    the two journals cleanly separated.
    """

    _name = "school_enrollment"
    _inherit = [
        "school_enrollment",
    ]

    scholarship_award_ids = fields.One2many(
        string="Scholarship Awards",
        comodel_name="school_scholarship_award",
        inverse_name="enrollment_id",
        help="Scholarship awards linked to this enrollment.",
    )
    amount_scholarship = fields.Monetary(
        string="Scholarship Amount",
        compute="_compute_amount_scholarship",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        groups="ssi_school_scholarship.school_scholarship_award_viewer_group",
        help=(
            "Total amount awarded by this enrollment's Open or Done "
            "scholarship awards. A commitment figure, not a "
            "realization -- realization becomes available once the "
            "deduction module ships. Restricted to the Scholarship "
            "Award Viewer group."
        ),
    )
    scholarship_award_count = fields.Integer(
        string="Scholarship Award Count",
        compute="_compute_scholarship_award_count",
        store=False,
        compute_sudo=True,
        help="Number of scholarship awards linked to this enrollment.",
    )

    @api.depends(
        "scholarship_award_ids.state",
        "scholarship_award_ids.amount_awarded",
    )
    def _compute_amount_scholarship(self):
        """Sum the awarded amount of Open or Done scholarship awards.

        :return: nothing; assigns ``amount_scholarship``
        """
        for record in self:
            result = 0.0
            awards = record.scholarship_award_ids.filtered(
                lambda award: award.state in ("open", "done")
            )
            if awards:
                result = sum(awards.mapped("amount_awarded"))
            record.amount_scholarship = result

    @api.depends("scholarship_award_ids")
    def _compute_scholarship_award_count(self):
        """Count the scholarship awards linked to this enrollment.

        :return: nothing; assigns ``scholarship_award_count``
        """
        for record in self:
            record.scholarship_award_count = len(record.scholarship_award_ids)

    def action_open_scholarship_award(self):
        """Open the list of scholarship awards linked to this enrollment.

        :return: an ``ir.actions.act_window`` dict
        """
        for record in self.sudo():
            result = record._open_scholarship_award()
        return result

    def _open_scholarship_award(self):
        """Build the window action listing this enrollment's awards.

        :return: an ``ir.actions.act_window`` dict limited to the
            scholarship awards of this enrollment
        """
        self.ensure_one()
        waction = self.env.ref(
            "ssi_school_scholarship.school_scholarship_award_action"
        ).read()[0]
        waction.update(
            {
                "domain": [("enrollment_id", "=", self.id)],
                "context": {"default_enrollment_id": self.id},
            }
        )
        return waction
