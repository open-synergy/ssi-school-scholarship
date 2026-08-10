# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolScholarshipAward(models.Model):
    """Extend School Scholarship Award with an Admission billing source.

    Registers ``admission`` as a second ``source_type`` value, alongside
    the base module's ``enrollment``, so a scholarship award can also be
    granted against a ``school_admission`` that has already reached
    state Open (the point at which ``school_admission`` creates its own
    ``school_student_id``). All ``_get_source_*``/schedule hooks fall
    back to ``super()`` whenever ``source_type`` is not ``admission``,
    so enrollment-sourced awards keep working unmodified.
    """

    _name = "school_scholarship_award"
    _inherit = [
        "school_scholarship_award",
    ]

    source_type = fields.Selection(
        selection_add=[
            ("admission", "Admission"),
        ],
        ondelete={"admission": "set default"},
    )
    admission_id = fields.Many2one(
        string="Admission",
        comodel_name="school_admission",
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        domain=[("state", "in", ["open", "done"])],
        help="Admission this award is billed against. Must already be "
        "Open or Done -- an admission earlier than Open has not yet "
        "created its School Student, so it cannot be billed against. "
        "Required when Billing Source is Admission -- enforced by "
        "``_check_billing_source``, not by this field itself.",
    )

    @api.depends("enrollment_id", "admission_id")
    def _compute_school_id(self):
        """Widen the School computation's dependencies to Admission.

        Odoo does not merge ``@api.depends`` across an inherited
        method's redefinitions -- only the decorator on the final
        method in the MRO takes effect -- so ``admission_id`` must be
        declared here for a change to it to retrigger this compute.
        The body itself is unchanged: ``super()`` already goes
        through ``_get_source_record()``, which this module overrides
        to resolve ``admission_id`` too.

        :return: whatever ``super()._compute_school_id()`` returns
        """
        return super()._compute_school_id()

    @api.depends("enrollment_id", "admission_id")
    def _compute_grade_id(self):
        """Widen the Grade computation's dependencies to Admission.

        See ``_compute_school_id`` for why this redeclaration is
        needed and why the body only forwards to ``super()``.

        :return: whatever ``super()._compute_grade_id()`` returns
        """
        return super()._compute_grade_id()

    @api.constrains("source_type", "enrollment_id", "admission_id")
    def _check_billing_source(self):
        """Widen the billing source check's dependencies to Admission.

        The check itself (``_get_source_record()`` must be non-empty)
        is unchanged; only the trigger fields are widened so editing
        ``admission_id`` re-runs it. See ``_compute_school_id`` for
        why the redeclaration is needed.

        :return: whatever ``super()._check_billing_source()`` returns
        """
        return super()._check_billing_source()

    @api.constrains("company_currency_id", "enrollment_id", "admission_id")
    def _check_currency(self):
        """Widen the currency check's dependencies to Admission.

        See ``_compute_school_id`` for why this redeclaration is
        needed and why the body only forwards to ``super()``.

        :return: whatever ``super()._check_currency()`` returns
        """
        return super()._check_currency()

    @api.constrains("admission_id", "student_id")
    def _check_admission_student(self):
        """Require the Admission to already have a matching Student.

        Rejects an Admission that has not yet reached state Open (its
        ``school_student_id`` is still empty -- the admission has not
        created a School Student yet), and rejects one whose School
        Student does not match this award's own Student.

        :raises ValidationError: when ``admission_id`` is set and
            either its ``school_student_id`` is empty or differs from
            ``student_id``.
        """
        for record in self:
            if not record.admission_id:
                continue
            admission_student = record.admission_id.school_student_id
            if not admission_student:
                error_message = """
Document Type: %s
Context: Select award admission
Database ID: %s
Problem: Admission '%s' has not reached Open yet, so it has no School Student
Solution: Select an Admission already Open or Done
""" % (
                    self._description,
                    record.id,
                    record.admission_id.display_name,
                )
                raise ValidationError(_(error_message))
            if admission_student != record.student_id:
                error_message = """
Document Type: %s
Context: Select award admission
Database ID: %s
Problem: Admission '%s' does not belong to Student '%s'
Solution: Select an Admission whose School Student matches the selected Student
""" % (
                    self._description,
                    record.id,
                    record.admission_id.display_name,
                    record.student_id.name,
                )
                raise ValidationError(_(error_message))

    @api.onchange("admission_id")
    def onchange_student_id(self):
        """Default Student from the selected Admission's School Student."""
        self.student_id = False
        if self.admission_id:
            self.student_id = self.admission_id.school_student_id

    def _get_source_record(self):
        """Return the Admission when Billing Source is Admission.

        :return: ``self.admission_id`` when ``source_type`` is
            ``admission``, otherwise whatever ``super()`` returns
        """
        self.ensure_one()
        if self.source_type == "admission":
            return self.admission_id
        return super()._get_source_record()

    def _get_source_payment_terms(self):
        """Return the Admission's payment terms for an Admission award.

        :return: ``school_admission_payment_term`` recordset when
            ``source_type`` is ``admission``, otherwise whatever
            ``super()`` returns
        """
        self.ensure_one()
        if self.source_type == "admission":
            return self.admission_id.payment_term_ids
        return super()._get_source_payment_terms()

    def _get_source_currency(self):
        """Return the Admission's currency for an Admission award.

        :return: ``res.currency`` record when ``source_type`` is
            ``admission``, otherwise whatever ``super()`` returns
        """
        self.ensure_one()
        if self.source_type == "admission":
            return self.admission_id.currency_id
        return super()._get_source_currency()

    def _get_schedule_term_domain(self, benefit, term):
        """Match a Schedule line by ``admission_payment_term_id``.

        :param benefit: the ``school_scholarship_award_benefit``
            record being scheduled
        :param term: the payment term record being realized
        :return: a search domain list matching on
            ``admission_payment_term_id`` when ``source_type`` is
            ``admission``, otherwise whatever ``super()`` returns
        """
        self.ensure_one()
        if self.source_type == "admission":
            return [
                ("benefit_id", "=", benefit.id),
                ("admission_payment_term_id", "=", term.id),
            ]
        return super()._get_schedule_term_domain(benefit, term)

    def _prepare_schedule_term_data(self, payment_term):
        """Carry the Admission payment term onto a new Schedule line.

        :param payment_term: the payment term record being realized
        :return: dict setting ``admission_payment_term_id`` when
            ``source_type`` is ``admission``, otherwise whatever
            ``super()`` returns
        """
        self.ensure_one()
        if self.source_type == "admission":
            return {"admission_payment_term_id": payment_term.id}
        return super()._prepare_schedule_term_data(payment_term)
