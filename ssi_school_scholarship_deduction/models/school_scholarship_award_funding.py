# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SchoolScholarshipAwardFunding(models.Model):
    """
    Extends the award Funding line with a readable display name.

    ``school_scholarship_award_funding`` has no ``name`` field of its
    own, so its default display name is the unreadable ``"<model>,
    <id>"`` fallback -- unusable for picking a specific Funding line
    on a deduction line's own ``funding_id`` Many2one, which several
    Funding lines of the same Award (one per funding split) must be
    told apart in. This composes one from the Funding Source's own
    name and this line's Percentage instead.
    """

    _inherit = "school_scholarship_award_funding"

    def name_get(self):
        """Compose a display name from Funding Source and Percentage.

        :return: list of ``(id, name)`` tuples
        """
        result = []
        for record in self:
            name = "%s (%.0f%%)" % (
                record.funding_source_id.display_name,
                record.percentage,
            )
            result.append((record.id, name))
        return result
