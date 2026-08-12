# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase -- NOT HttpCase. In 14.0, HttpCase does not set up
# cls.env in setUpClass, so fixtures written there would fail with
# AttributeError before the browser even starts.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiSchoolScholarshipDeduction(HttpSavepointCase):
    """Tour tests for the ``school_scholarship_deduction`` work
    instructions.
    """

    @classmethod
    def setUpClass(cls):
        """Create the master data and deductions required by the tours."""
        super().setUpClass()
        admin = cls.env.ref("base.user_admin")
        account_type_income = cls.env.ref("account.data_account_type_revenue")
        account_type_receivable = cls.env.ref("account.data_account_type_receivable")
        account_type_asset = cls.env.ref("account.data_account_type_current_assets")

        # Pre-Condition -- School/Academic Year/Grade/Grade
        # Class/Student, so an Enrollment can be created for the tour
        # Student.
        tour_grade_type = cls.env["school_grade_type"].create(
            {
                "name": "TOUR Deduction Grade Type",
                "code": "TOURDDGT",
            }
        )
        tour_school = cls.env["school"].create(
            {
                "name": "TOUR Deduction School",
                "code": "TOURDDS",
                "grade_type_id": tour_grade_type.id,
            }
        )
        tour_academic_year = cls.env["school_academic_year"].create(
            {
                "name": "TOUR Deduction Academic Year",
                "code": "TOURDDY",
                "date_start": "2026-07-01",
                "date_end": "2027-06-30",
            }
        )
        tour_academic_term = cls.env["school_academic_term"].create(
            {
                "name": "TOUR Deduction Academic Term",
                "code": "TOURDDTM",
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
                "year_id": tour_academic_year.id,
            }
        )
        tour_grade = cls.env["school_grade"].create(
            {
                "name": "TOUR Deduction Grade",
                "code": "TOURDDG",
                "type_id": tour_grade_type.id,
            }
        )
        tour_grade_class = cls.env["school_grade_class"].create(
            {
                "name": "TOUR Deduction Grade Class",
                "code": "TOURDDGC",
                "school_id": tour_school.id,
                "grade_id": tour_grade.id,
            }
        )
        tour_contact = cls.env["res.partner"].create(
            {
                "name": "TOUR Deduction Student Contact",
            }
        )
        tour_student = cls.env["school_student"].create(
            {
                "name": "TOUR Deduction Student",
                "code": "TOURDDST",
                "contact_id": tour_contact.id,
                "school_id": tour_school.id,
            }
        )
        tour_enrollment = cls.env["school_enrollment"].create(
            {
                "name": "TOUR-DEDUCTION-ENR-001",
                "academic_year_id": tour_academic_year.id,
                "academic_term_id": tour_academic_term.id,
                "school_id": tour_school.id,
                "grade_id": tour_grade.id,
                "grade_class_id": tour_grade_class.id,
                "student_id": tour_student.id,
            }
        )

        # Pre-Condition -- a Funding Source, a Product, a Program with
        # one Scope line, and a Journal/Receivable/Discount account
        # trio, so an Award (and the invoices below) can be built.
        tour_analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "TOUR Deduction Analytic",
            }
        )
        tour_funding_source = cls.env["school_scholarship_funding_source"].create(
            {
                "name": "TOUR Deduction Funding Source",
                "code": "TOURDDF",
                "analytic_account_id": tour_analytic_account.id,
            }
        )
        tour_product = cls.env["product.product"].create(
            {
                "name": "TOUR Deduction Product",
                "type": "service",
            }
        )
        tour_journal = cls.env["account.journal"].create(
            {
                "name": "TOUR Deduction Sale Journal",
                "code": "TDDJ",
                "type": "sale",
            }
        )
        tour_receivable_account = cls.env["account.account"].create(
            {
                "name": "TOUR Deduction Receivable Account",
                "code": "TOURDDRA",
                "user_type_id": account_type_receivable.id,
                "reconcile": True,
            }
        )
        tour_discount_account = cls.env["account.account"].create(
            {
                "name": "TOUR Deduction Discount Account",
                "code": "TOURDDDA",
                "user_type_id": account_type_income.id,
                "reconcile": False,
            }
        )
        tour_income_account = cls.env["account.account"].create(
            {
                "name": "TOUR Deduction Income Account",
                "code": "TOURDDIA",
                "user_type_id": account_type_income.id,
                "reconcile": False,
            }
        )
        tour_invoice_type = cls.env["customer_invoice_type"].create(
            {
                "name": "TOUR Deduction Invoice Type",
                "code": "/",
                "journal_id": tour_journal.id,
                "receivable_account_id": tour_receivable_account.id,
            }
        )
        tour_type = cls.env["school_scholarship_type"].create(
            {
                "name": "TOUR Deduction Scholarship Type",
                "code": "TOURDDTY",
                "deduction_journal_id": tour_journal.id,
                "discount_account_id": tour_discount_account.id,
            }
        )
        tour_program = cls.env["school_scholarship_program"].create(
            {
                "name": "TOUR Deduction Program",
                "code": "TOURDDPRG",
                "type_id": tour_type.id,
                "school_id": tour_school.id,
                "academic_year_id": tour_academic_year.id,
                "funding_source_ids": [(6, 0, [tour_funding_source.id])],
                "deduction_journal_id": tour_journal.id,
                "discount_account_id": tour_discount_account.id,
                "scope_ids": [
                    (
                        0,
                        0,
                        {
                            "scope_basis": "product",
                            "product_id": tour_product.id,
                            "benefit_type": "cash",
                            "computation": "fixed",
                            "amount_fixed": 100000.0,
                        },
                    )
                ],
            }
        )

        def _make_award(name, amount, program=None):
            """Build an Award with one Cash Benefit and Funding line.

            :param name: unique name assigned to the Award
            :param amount: fixed amount of the Award's own Benefit
                line, also its Schedule line's Amount Planned
            :param program: ``school_scholarship_program`` to link;
                defaults to ``tour_program`` when not given
            :return: the created ``school_scholarship_award`` record,
                its Benefit, Funding, and Schedule lines
            """
            award = cls.env["school_scholarship_award"].create(
                {
                    "name": name,
                    "program_id": (program or tour_program).id,
                    "student_id": tour_student.id,
                    "enrollment_id": tour_enrollment.id,
                    "date_start": "2026-07-01",
                    "date_end": "2026-12-31",
                    # school_scholarship_award_benefit._compute_account_id
                    # reads this directly off the Award (not through any
                    # onchange chain) for a Benefit with benefit_type
                    # "cash", as created below. create() here never runs
                    # the form's own onchange_expense_account_id (that
                    # only fires in the real web client), so without this
                    # the Benefit's own account_id -- and, through the
                    # deduction Line's onchange_final_account_id, the
                    # deduction Line's own Final Account -- would compute
                    # to False, leaving that required field empty and
                    # the Line permanently invalid for the browser to
                    # commit.
                    "expense_account_id": tour_discount_account.id,
                    "benefit_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "%s Benefit" % name,
                                "product_id": tour_product.id,
                                "benefit_type": "cash",
                                "computation": "fixed",
                                "amount_fixed": amount,
                                "periodicity": "one_time",
                            },
                        )
                    ],
                    "funding_ids": [
                        (
                            0,
                            0,
                            {
                                "funding_source_id": tour_funding_source.id,
                                "percentage": 100.0,
                            },
                        )
                    ],
                }
            )
            benefit = award.benefit_ids[:1]
            funding = award.funding_ids[:1]
            schedule = cls.env["school_scholarship_award_schedule"].create(
                {
                    "benefit_id": benefit.id,
                    "date": "2026-08-01",
                    "state": "scheduled",
                }
            )
            return award, benefit, funding, schedule

        def _make_open_invoice(name, amount):
            """Build and open a customer invoice with one line.

            :param name: this invoice's own document number, set
                explicitly here rather than left at the "/" default --
                ``mixin.sequence._create_sequence`` only replaces the
                name with an auto-generated sequence when it is still
                exactly the template's initial string ("/"), so setting
                it up front makes it permanent and lets the "create"
                tour find this exact invoice by name through the
                ``customer_invoice_id`` many2one's autocomplete. Also
                used as a prefix for the invoice line's own label.
            :param amount: the invoice line's Price Unit, also the
                resulting invoice's own residual once opened
            :return: the opened ``customer_invoice`` record

            Must be unique not just among invoices but across every
            OTHER posted transactional document in this file too:
            ``mixin.account_move`` posts each document's own journal
            entry using that document's own ``name`` as the entry's
            ``name`` (``_number_field_name`` defaults to ``"name"``),
            and Odoo's ``account.move`` rejects two POSTED entries
            sharing one name in the same company ("Posted journal
            entry must have an unique sequence number per company").
            An invoice and a ``school_scholarship_deduction`` that
            both reach a posted state -- as the 05-approve fixture's
            invoice and deduction both do -- collide if they share a
            literal name, even though they are different models.
            """
            invoice = cls.env["customer_invoice"].create(
                {
                    "name": name,
                    "type_id": tour_invoice_type.id,
                    "partner_id": tour_contact.id,
                    "date": "2026-08-01",
                    "date_due": "2026-08-15",
                    "currency_id": cls.env.company.currency_id.id,
                    "journal_id": tour_journal.id,
                    "receivable_account_id": tour_receivable_account.id,
                    "user_id": admin.id,
                }
            )
            cls.env["customer_invoice.line"].create(
                {
                    "customer_invoice_id": invoice.id,
                    "name": "%s Invoice Line" % name,
                    "account_id": tour_income_account.id,
                    "uom_quantity": 1,
                    "price_unit": amount,
                }
            )
            invoice.action_confirm()
            invoice.invalidate_cache()
            invoice.with_user(admin).action_approve_approval()
            return invoice

        # Pre-Condition for 01-create -- an Award (with Schedule and
        # Funding to pick from) and an open invoice to allocate
        # against, so the tour has something to select on both tabs.
        (
            cls.tour_award_create,
            _tour_benefit_create,
            _tour_funding_create,
            cls.tour_schedule_create,
        ) = _make_award("TOUR-DEDUCTION-AWARD-CREATE-001", 400000.0)
        cls.tour_invoice_create = _make_open_invoice(
            "TOUR-DEDUCTION-CREATE-001", 1000000.0
        )

        # Pre-Condition for 04-confirm -- a Draft deduction with one
        # Line and one Allocation, so Confirm has something valid to
        # work on.
        (
            tour_award_confirm,
            tour_benefit_confirm,
            tour_funding_confirm,
            tour_schedule_confirm,
        ) = _make_award("TOUR-DEDUCTION-AWARD-CONFIRM-001", 400000.0)
        tour_invoice_confirm = _make_open_invoice(
            "TOUR-DEDUCTION-CONFIRM-INV-001", 1000000.0
        )
        cls.tour_deduction_confirm = cls.env["school_scholarship_deduction"].create(
            {
                "name": "TOUR-DEDUCTION-CONFIRM-001",
                "award_id": tour_award_confirm.id,
                "journal_id": tour_journal.id,
                "receivable_account_id": tour_receivable_account.id,
                "user_id": admin.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "schedule_id": tour_schedule_confirm.id,
                            "funding_id": tour_funding_confirm.id,
                            "final_account_id": tour_discount_account.id,
                            "name": "TOUR Deduction Confirm Line",
                            "uom_quantity": 1,
                            "price_unit": 400000.0,
                        },
                    )
                ],
                "allocation_ids": [
                    (
                        0,
                        0,
                        {
                            "customer_invoice_id": tour_invoice_confirm.id,
                            "amount_allocated": 400000.0,
                        },
                    )
                ],
            }
        )

        # Pre-Condition for 05-approve -- the same as above, but
        # already pushed to Waiting for Approval in Python via
        # ``action_confirm()``, since Confirm itself is exercised by
        # 04-confirm.md's own tour.
        (
            tour_award_approve,
            tour_benefit_approve,
            tour_funding_approve,
            tour_schedule_approve,
        ) = _make_award("TOUR-DEDUCTION-AWARD-APPROVE-001", 400000.0)
        tour_invoice_approve = _make_open_invoice(
            "TOUR-DEDUCTION-APPROVE-INV-001", 1000000.0
        )
        cls.tour_deduction_approve = cls.env["school_scholarship_deduction"].create(
            {
                "name": "TOUR-DEDUCTION-APPROVE-001",
                "award_id": tour_award_approve.id,
                "journal_id": tour_journal.id,
                "receivable_account_id": tour_receivable_account.id,
                "user_id": admin.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "schedule_id": tour_schedule_approve.id,
                            "funding_id": tour_funding_approve.id,
                            "final_account_id": tour_discount_account.id,
                            "name": "TOUR Deduction Approve Line",
                            "uom_quantity": 1,
                            "price_unit": 400000.0,
                        },
                    )
                ],
                "allocation_ids": [
                    (
                        0,
                        0,
                        {
                            "customer_invoice_id": tour_invoice_approve.id,
                            "amount_allocated": 400000.0,
                        },
                    )
                ],
            }
        )
        cls.tour_deduction_approve.action_confirm()
        # ``approve_ok`` shares its compute method (``_compute_policy``)
        # with every other policy field, and that method only
        # re-triggers on ``@api.depends("policy_template_id")`` --
        # confirming already cached approve_ok=False (no approver
        # existed yet), so it must be busted explicitly before
        # Approve reads it (odoo-development-unit-test,
        # test-traps.md T-04, same fix already applied in
        # test_data_school_scholarship_deduction.yaml).
        cls.tour_deduction_approve.invalidate_cache()

        # Pre-Condition for 10-cancel -- a Draft deduction, plus the
        # Cancellation Reason the wizard requires. No Line/Allocation
        # is needed: cancelling a Draft document never reaches the
        # accounting hooks at all.
        (
            tour_award_cancel,
            _tour_benefit_cancel,
            _tour_funding_cancel,
            _tour_schedule_cancel,
        ) = _make_award("TOUR-DEDUCTION-AWARD-CANCEL-001", 400000.0)
        cls.tour_deduction_cancel = cls.env["school_scholarship_deduction"].create(
            {
                "name": "TOUR-DEDUCTION-CANCEL-001",
                "award_id": tour_award_cancel.id,
                "journal_id": tour_journal.id,
                "receivable_account_id": tour_receivable_account.id,
                "user_id": admin.id,
            }
        )
        cls.env["base.cancel_reason"].create(
            {
                "name": "TOUR Deduction Cancel Reason",
                "code": "TOURDDCR",
                # The cancel wizard's radio widget only lists reasons
                # in ir.model.all_cancel_reason_ids, which merges
                # model-specific links with every global_use=True
                # reason. Without this, the tour's radio option never
                # renders (0 matches on the trigger selector) since
                # this reason is not linked to any specific model.
                "global_use": True,
            }
        )

        # Pre-Condition for 06-create-due-recognition -- an Open
        # Deduction whose own Recognition Method computes to Deferred
        # (its own Date is earlier than its Award's Start Date) and
        # is still Pending (nothing recognized yet), so the wizard's
        # own due-search picks it up. A dedicated Program with
        # ``allow_asymmetric_recognition`` is needed because the
        # allocated invoice below still books straight to an
        # Income-type account -- otherwise
        # ``_check_recognition_symmetry`` rejects a Deferred deduction
        # outright (mirrors the identical fixture already proven in
        # ``test_school_scholarship_deduction_recognition.py``'s own
        # ``test_wizard_create_due_recognition``).
        tour_deferred_account = cls.env["account.account"].create(
            {
                "name": "TOUR Deduction Deferred Account",
                "code": "TOURDDFA",
                "user_type_id": account_type_asset.id,
                "reconcile": False,
            }
        )
        tour_program_recognition = cls.env["school_scholarship_program"].create(
            {
                "name": "TOUR Deduction Recognition Program",
                "code": "TOURDDRPRG",
                "type_id": tour_type.id,
                "school_id": tour_school.id,
                "academic_year_id": tour_academic_year.id,
                "funding_source_ids": [(6, 0, [tour_funding_source.id])],
                "deduction_journal_id": tour_journal.id,
                "discount_account_id": tour_discount_account.id,
                "allow_asymmetric_recognition": True,
                "scope_ids": [
                    (
                        0,
                        0,
                        {
                            "scope_basis": "product",
                            "product_id": tour_product.id,
                            "benefit_type": "cash",
                            "computation": "fixed",
                            "amount_fixed": 100000.0,
                        },
                    )
                ],
            }
        )
        (
            tour_award_recognition,
            _tour_benefit_recognition,
            tour_funding_recognition,
            tour_schedule_recognition,
        ) = _make_award(
            "TOUR-DEDUCTION-AWARD-RECOGNITION-001",
            400000.0,
            program=tour_program_recognition,
        )
        tour_invoice_recognition = _make_open_invoice(
            "TOUR-DEDUCTION-RECOGNITION-INV-001", 1000000.0
        )
        cls.tour_deduction_recognition = cls.env["school_scholarship_deduction"].create(
            {
                "name": "TOUR-DEDUCTION-RECOGNITION-001",
                "award_id": tour_award_recognition.id,
                # Earlier than the Award's own Start Date (2026-07-01,
                # hardcoded in ``_make_award``) so
                # ``_compute_recognition_date`` picks the Award's
                # Start Date instead, landing after this document's
                # own Date and making ``_compute_recognition_method``
                # resolve to Deferred.
                "date": "2026-01-01",
                "journal_id": tour_journal.id,
                "receivable_account_id": tour_receivable_account.id,
                "deferred_account_id": tour_deferred_account.id,
                "recognition_journal_id": tour_journal.id,
                "user_id": admin.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "schedule_id": tour_schedule_recognition.id,
                            "funding_id": tour_funding_recognition.id,
                            "final_account_id": tour_discount_account.id,
                            "name": "TOUR Deduction Recognition Line",
                            "uom_quantity": 1,
                            "price_unit": 400000.0,
                        },
                    )
                ],
                "allocation_ids": [
                    (
                        0,
                        0,
                        {
                            "customer_invoice_id": tour_invoice_recognition.id,
                            "amount_allocated": 400000.0,
                        },
                    )
                ],
            }
        )
        cls.tour_deduction_recognition.action_confirm()
        # Same cache-busting need as the 05-approve fixture above --
        # ``approve_ok`` is cached from confirming before an approver
        # existed. ``with_user(admin)`` is required too, same as the
        # invoice fixture above: the policy expression backing
        # ``approve_ok`` (policy_template/school_scholarship_deduction
        # .xml) reads ``env.user.id in
        # document.active_approver_user_ids.ids``, so it must be
        # recomputed as the approver, not as whichever user
        # ``cls.env`` defaults to.
        cls.tour_deduction_recognition.invalidate_cache()
        cls.tour_deduction_recognition.with_user(admin).action_approve_approval()

    def test_create(self):
        """Run the create tour for ``school_scholarship_deduction``.

        IK: docs/school_scholarship_deduction/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_deduction_school_scholarship_deduction_create",
            login="admin",
        )

    def test_confirm(self):
        """Run the confirm tour for ``school_scholarship_deduction``.

        IK: docs/school_scholarship_deduction/04-confirm.md
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_deduction_school_scholarship_deduction_confirm",
            login="admin",
        )

    def test_approve(self):
        """Run the approve tour for ``school_scholarship_deduction``.

        IK: docs/school_scholarship_deduction/05-approve.md
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_deduction_school_scholarship_deduction_approve",
            login="admin",
        )

    def test_cancel(self):
        """Run the cancel tour for ``school_scholarship_deduction``.

        IK: docs/school_scholarship_deduction/10-cancel.md
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_deduction_school_scholarship_deduction_cancel",
            login="admin",
        )

    def test_create_due_recognition(self):
        """Run the due-recognition tour for ``school_scholarship_deduction``.

        IK: docs/school_scholarship_deduction/06-create-due-recognition.md
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_deduction_school_scholarship_deduction_"
            "create_due_recognition",
            login="admin",
        )
