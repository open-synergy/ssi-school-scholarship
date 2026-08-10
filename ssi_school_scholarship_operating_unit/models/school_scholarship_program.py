# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SchoolScholarshipProgram(models.Model):  # pylint: disable=too-few-public-methods
    """
    Extends School Scholarship Program with multiple operating unit support
    for operating unit-based data segregation.
    """

    _name = "school_scholarship_program"
    _inherit = [
        "school_scholarship_program",
        "mixin.multiple_operating_unit",
    ]
