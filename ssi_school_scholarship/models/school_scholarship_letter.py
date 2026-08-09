# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SchoolScholarshipLetter(models.Model):
    """
    Represents one letter related to a scholarship award (award letter,
    agreement, revocation letter, or renewal letter).
    Only the letter's metadata is recorded here — the physical file
    (a scan of the signed letter, for instance) is attached on this
    record's own chatter, via ``mail.thread``, rather than stored as
    a Binary field.
    """

    _name = "school_scholarship_letter"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
    ]
    _description = "School Scholarship Letter"
    _order = "date desc, id desc"

    award_id = fields.Many2one(
        string="Award",
        comodel_name="school_scholarship_award",
        required=True,
        ondelete="cascade",
        help="Scholarship award this letter belongs to.",
    )
    letter_type = fields.Selection(
        string="Letter Type",
        selection=[
            ("award_letter", "Award Letter"),
            ("agreement", "Agreement"),
            ("revocation", "Revocation Letter"),
            ("renewal", "Renewal Letter"),
        ],
        required=True,
        help="Kind of letter this record represents.",
    )
    date = fields.Date(
        string="Date",
        required=True,
        help="Date the letter was issued.",
    )
    date_signed = fields.Date(
        string="Date Signed",
        help="Date the letter was signed, if already signed.",
    )
    signed_by = fields.Char(
        string="Signed By",
        help="Name of the person who signed the letter.",
    )
    note = fields.Text(
        string="Note",
        help="Free-form note about this letter.",
    )
