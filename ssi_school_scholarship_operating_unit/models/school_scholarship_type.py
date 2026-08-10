# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SchoolScholarshipType(models.Model):  # pylint: disable=too-few-public-methods
    """
    Extends School Scholarship Type with multiple operating unit support
    for operating unit-based data segregation.
    """

    _name = "school_scholarship_type"
    _inherit = [
        "school_scholarship_type",
        "mixin.multiple_operating_unit",
    ]
