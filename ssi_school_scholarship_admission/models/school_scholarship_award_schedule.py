# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SchoolScholarshipAwardSchedule(models.Model):
    """Extend Schedule with an Admission Payment Term source field.

    Gives a Schedule line a second, mutually-exclusive source term
    field, ``admission_payment_term_id``, alongside the base module's
    ``payment_term_id`` (an enrollment payment term). All
    ``_get_source_term*`` hooks fall back to ``super()`` whenever
    ``admission_payment_term_id`` is empty, so enrollment-sourced
    Schedule lines keep working unmodified.
    """

    _name = "school_scholarship_award_schedule"
    _inherit = [
        "school_scholarship_award_schedule",
    ]

    admission_payment_term_id = fields.Many2one(
        string="Admission Payment Term",
        comodel_name="school_admission_payment_term",
        ondelete="restrict",
        help="Admission payment term this Schedule line realizes. Set "
        "instead of Payment Term when this line was generated from an "
        "Admission-sourced award.",
    )

    def _get_source_term(self):
        """Return the Admission payment term when one is set.

        :return: ``admission_payment_term_id`` when set, otherwise
            whatever ``super()`` returns
        """
        self.ensure_one()
        if self.admission_payment_term_id:
            return self.admission_payment_term_id
        return super()._get_source_term()

    def _get_source_term_parent(self):
        """Return the Admission owning the source term when one is set.

        :return: the Admission payment term's own ``admission_id``
            when set, otherwise whatever ``super()`` returns
        """
        self.ensure_one()
        if self.admission_payment_term_id:
            return self.admission_payment_term_id.admission_id
        return super()._get_source_term_parent()

    @api.depends(
        "payment_term_id",
        "payment_term_id.name",
        "admission_payment_term_id",
        "admission_payment_term_id.name",
        "date",
    )
    def _compute_name(self):
        """Widen the Name computation's dependencies to Admission.

        See ``school_scholarship_award._compute_school_id`` (glue
        module ``ssi_school_scholarship_admission``) for why this
        redeclaration -- widening ``@api.depends``, forwarding the
        body to ``super()`` -- is needed.

        :return: whatever ``super()._compute_name()`` returns
        """
        return super()._compute_name()

    @api.depends(
        "payment_term_id",
        "payment_term_id.detail_ids.price_subtotal",
        "payment_term_id.detail_ids.product_id",
        "payment_term_id.detail_ids.product_category_id",
        "payment_term_id.detail_ids.voided",
        "admission_payment_term_id",
        "admission_payment_term_id.detail_ids.price_subtotal",
        "admission_payment_term_id.detail_ids.product_id",
        "admission_payment_term_id.detail_ids.product_category_id",
        "admission_payment_term_id.detail_ids.voided",
        "benefit_id.product_id",
        "benefit_id.product_category_id",
    )
    def _compute_base_amount(self):
        """Widen the Base Amount computation's dependencies.

        See ``_compute_name`` above for why this redeclaration is
        needed.

        :return: whatever ``super()._compute_base_amount()`` returns
        """
        return super()._compute_base_amount()

    @api.depends(
        "payment_term_id",
        "payment_term_id.state",
        "admission_payment_term_id",
        "admission_payment_term_id.state",
    )
    def _compute_payment_term_state(self):
        """Widen the Payment Term State computation's dependencies.

        See ``_compute_name`` above for why this redeclaration is
        needed.

        :return: whatever ``super()._compute_payment_term_state()``
            returns
        """
        return super()._compute_payment_term_state()

    @api.depends(
        "payment_term_id",
        "payment_term_id.customer_invoice_id",
        "admission_payment_term_id",
        "admission_payment_term_id.customer_invoice_id",
    )
    def _compute_customer_invoice_id(self):
        """Widen the Customer Invoice computation's dependencies.

        See ``_compute_name`` above for why this redeclaration is
        needed.

        :return: whatever ``super()._compute_customer_invoice_id()``
            returns
        """
        return super()._compute_customer_invoice_id()

    @api.constrains("benefit_id", "payment_term_id", "admission_payment_term_id")
    def _check_duplicate_benefit_payment_term(self):
        """Widen the duplicate-term check's dependencies to Admission.

        See ``_compute_name`` above for why this redeclaration is
        needed.

        :return: whatever
            ``super()._check_duplicate_benefit_payment_term()``
            returns
        """
        return super()._check_duplicate_benefit_payment_term()

    @api.constrains("benefit_id", "payment_term_id", "admission_payment_term_id")
    def _check_payment_term_required(self):
        """Widen the required-term check's dependencies to Admission.

        See ``_compute_name`` above for why this redeclaration is
        needed.

        :return: whatever ``super()._check_payment_term_required()``
            returns
        """
        return super()._check_payment_term_required()

    @api.constrains("payment_term_id", "admission_payment_term_id", "award_id")
    def _check_payment_term_enrollment(self):
        """Widen the source-term-ownership check's dependencies.

        See ``_compute_name`` above for why this redeclaration is
        needed.

        :return: whatever ``super()._check_payment_term_enrollment()``
            returns
        """
        return super()._check_payment_term_enrollment()
