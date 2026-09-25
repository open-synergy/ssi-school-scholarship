# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SchoolEnrollmentRevenueRecognitionLine(models.Model):
    # Extension: adds the originating scholarship deduction line,
    # mirroring the base module's own ``payment_term_detail_id``, for
    # a Recognition Line generated for an enrollment-mode scholarship
    # deduction rather than for an invoiced payment term detail.

    _name = "school_enrollment_revenue_recognition_line"
    _inherit = [
        "school_enrollment_revenue_recognition_line",
    ]

    scholarship_deduction_line_id = fields.Many2one(
        string="Scholarship Deduction Line",
        comodel_name="school_scholarship_deduction_line",
        ondelete="restrict",
        help=(
            "The enrollment-mode scholarship deduction line released "
            "by this Recognition Line, when it originates from a "
            "scholarship deduction rather than an invoiced payment "
            "term detail."
        ),
    )
