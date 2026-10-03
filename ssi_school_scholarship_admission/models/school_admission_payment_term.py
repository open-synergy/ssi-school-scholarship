# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class SchoolAdmissionPaymentTerm(models.Model):
    # Extension of the admission payment term: refuses deleting a
    # term that a scholarship award Schedule line refers to.
    _name = "school_admission_payment_term"
    _inherit = [
        "school_admission_payment_term",
    ]

    def _check_scholarship_award_reference(self):
        """Reject deleting a payment term referred to by an award.

        Looks for a scholarship award Schedule line pinned to one of
        these terms. The state of the award does not matter: the
        database foreign key is ``restrict`` regardless of state.

        :raises UserError: naming the first referring award and the
            payment term it refers to.
        :return: None
        """
        if not self.ids:
            return
        schedule = (
            self.env["school_scholarship_award_schedule"]
            .sudo()
            .search(
                [("admission_payment_term_id", "in", self.ids)],
                limit=1,
            )
        )
        if schedule:
            term = schedule.admission_payment_term_id
            error_message = """
Document Type: %s
Context: Delete admission payment term
Database ID: %s
Problem: Payment term '%s' is referenced by scholarship award '%s'
Solution: Cancel the scholarship award before deleting its payment terms
""" % (
                self._description,
                term.id,
                term.display_name,
                schedule.award_id.display_name,
            )
            raise UserError(_(error_message))

    def unlink(self):
        """Refuse deleting payment terms referred to by an award.

        Guarding ``unlink`` (rather than the Compute Payment button)
        covers Compute Payment, the Copy Payment Term wizard, and
        manual deletion of a row in a single place.

        :raises UserError: when an award Schedule line refers to a
            deleted term.
        :return: ``True``
        """
        self._check_scholarship_award_reference()
        return super().unlink()
