# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase -- NOT HttpCase. In 14.0, HttpCase does not set up
# cls.env in setUpClass, so fixtures written there would fail with
# AttributeError before the browser even starts.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiSchoolScholarshipDisbursement(HttpSavepointCase):
    """Tour tests for the ``school_scholarship_disbursement`` work
    instructions.
    """

    @classmethod
    def setUpClass(cls):
        """Create the master data and disbursements required by the
        tours.
        """
        super().setUpClass()
        admin = cls.env.ref("base.user_admin")
        account_type_expense = cls.env.ref("account.data_account_type_expenses")
        account_type_payable = cls.env.ref("account.data_account_type_payable")

        # Pre-Condition -- School/Academic Year/Grade/Grade
        # Class/Student, so an Enrollment can be created for the tour
        # Student.
        tour_grade_type = cls.env["school_grade_type"].create(
            {
                "name": "TOUR Disbursement Grade Type",
                "code": "TOURDBGT",
            }
        )
        tour_school = cls.env["school"].create(
            {
                "name": "TOUR Disbursement School",
                "code": "TOURDBS",
                "grade_type_id": tour_grade_type.id,
            }
        )
        tour_academic_year = cls.env["school_academic_year"].create(
            {
                "name": "TOUR Disbursement Academic Year",
                "code": "TOURDBY",
                "date_start": "2026-07-01",
                "date_end": "2027-06-30",
            }
        )
        tour_academic_term = cls.env["school_academic_term"].create(
            {
                "name": "TOUR Disbursement Academic Term",
                "code": "TOURDBTM",
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
                "year_id": tour_academic_year.id,
            }
        )
        tour_grade = cls.env["school_grade"].create(
            {
                "name": "TOUR Disbursement Grade",
                "code": "TOURDBG",
                "type_id": tour_grade_type.id,
            }
        )
        tour_grade_class = cls.env["school_grade_class"].create(
            {
                "name": "TOUR Disbursement Grade Class",
                "code": "TOURDBGC",
                "school_id": tour_school.id,
                "grade_id": tour_grade.id,
            }
        )
        tour_contact = cls.env["res.partner"].create(
            {
                "name": "TOUR Disbursement Student Contact",
            }
        )
        tour_student = cls.env["school_student"].create(
            {
                "name": "TOUR Disbursement Student",
                "code": "TOURDBST",
                "contact_id": tour_contact.id,
                "school_id": tour_school.id,
            }
        )
        tour_enrollment = cls.env["school_enrollment"].create(
            {
                "name": "TOUR-DISBURSEMENT-ENR-001",
                "academic_year_id": tour_academic_year.id,
                "academic_term_id": tour_academic_term.id,
                "school_id": tour_school.id,
                "grade_id": tour_grade.id,
                "grade_class_id": tour_grade_class.id,
                "student_id": tour_student.id,
            }
        )

        # Pre-Condition -- a Funding Source, a Product, a Program with
        # one Cash Scope line, and a Journal/Payable/Expense account
        # trio, so an Award can be built.
        tour_analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "TOUR Disbursement Analytic",
            }
        )
        tour_funding_source = cls.env["school_scholarship_funding_source"].create(
            {
                "name": "TOUR Disbursement Funding Source",
                "code": "TOURDBF",
                "analytic_account_id": tour_analytic_account.id,
            }
        )
        tour_product = cls.env["product.product"].create(
            {
                "name": "TOUR Disbursement Product",
                "type": "service",
            }
        )
        tour_journal = cls.env["account.journal"].create(
            {
                "name": "TOUR Disbursement Cash Journal",
                "code": "TDBJ",
                "type": "cash",
            }
        )
        tour_payable_account = cls.env["account.account"].create(
            {
                "name": "TOUR Disbursement Payable Account",
                "code": "TOURDBPA",
                "user_type_id": account_type_payable.id,
                "reconcile": True,
            }
        )
        tour_expense_account = cls.env["account.account"].create(
            {
                "name": "TOUR Disbursement Expense Account",
                "code": "TOURDBEA",
                "user_type_id": account_type_expense.id,
                "reconcile": False,
            }
        )
        tour_type = cls.env["school_scholarship_type"].create(
            {
                "name": "TOUR Disbursement Scholarship Type",
                "code": "TOURDBTY",
                "disbursement_journal_id": tour_journal.id,
                "payable_account_id": tour_payable_account.id,
            }
        )
        tour_program = cls.env["school_scholarship_program"].create(
            {
                "name": "TOUR Disbursement Program",
                "code": "TOURDBPRG",
                "type_id": tour_type.id,
                "school_id": tour_school.id,
                "academic_year_id": tour_academic_year.id,
                "funding_source_ids": [(6, 0, [tour_funding_source.id])],
                "disbursement_journal_id": tour_journal.id,
                "payable_account_id": tour_payable_account.id,
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

        def _make_award(name, amount):
            """Build an Award with one Cash Benefit and Funding line.

            :param name: unique name assigned to the Award
            :param amount: fixed amount of the Award's own Benefit
                line, also its Schedule line's Amount Planned
            :return: the created ``school_scholarship_award`` record,
                its Benefit, Funding, and Schedule lines
            """
            award = cls.env["school_scholarship_award"].create(
                {
                    "name": name,
                    "program_id": tour_program.id,
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
                    # disbursement Line's onchange_final_account_id, the
                    # disbursement Line's own Final Account -- would
                    # compute to False, leaving that required field
                    # empty and the Line permanently invalid for the
                    # browser to commit.
                    "expense_account_id": tour_expense_account.id,
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

        # Pre-Condition for 01-create -- an Award with Schedule and
        # Funding to pick from, so the tour has something to select on
        # the Lines tab.
        (
            cls.tour_award_create,
            _tour_benefit_create,
            _tour_funding_create,
            cls.tour_schedule_create,
        ) = _make_award("TOUR-DISBURSEMENT-AWARD-CREATE-001", 500000.0)

        # Pre-Condition for 04-confirm -- a Draft disbursement with
        # one Line, so Confirm has something valid to work on.
        (
            tour_award_confirm,
            tour_benefit_confirm,
            tour_funding_confirm,
            tour_schedule_confirm,
        ) = _make_award("TOUR-DISBURSEMENT-AWARD-CONFIRM-001", 500000.0)
        cls.tour_disbursement_confirm = cls.env[
            "school_scholarship_disbursement"
        ].create(
            {
                "name": "TOUR-DISBURSEMENT-CONFIRM-001",
                "award_id": tour_award_confirm.id,
                "journal_id": tour_journal.id,
                "payable_account_id": tour_payable_account.id,
                "payment_method": "cash",
                "date_due": "2026-08-15",
                "user_id": admin.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "schedule_id": tour_schedule_confirm.id,
                            "funding_id": tour_funding_confirm.id,
                            "final_account_id": tour_expense_account.id,
                            "name": "TOUR Disbursement Confirm Line",
                            "uom_quantity": 1,
                            "price_unit": 500000.0,
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
        ) = _make_award("TOUR-DISBURSEMENT-AWARD-APPROVE-001", 500000.0)
        cls.tour_disbursement_approve = cls.env[
            "school_scholarship_disbursement"
        ].create(
            {
                "name": "TOUR-DISBURSEMENT-APPROVE-001",
                "award_id": tour_award_approve.id,
                "journal_id": tour_journal.id,
                "payable_account_id": tour_payable_account.id,
                "payment_method": "cash",
                "date_due": "2026-08-15",
                "user_id": admin.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "schedule_id": tour_schedule_approve.id,
                            "funding_id": tour_funding_approve.id,
                            "final_account_id": tour_expense_account.id,
                            "name": "TOUR Disbursement Approve Line",
                            "uom_quantity": 1,
                            "price_unit": 500000.0,
                        },
                    )
                ],
            }
        )
        cls.tour_disbursement_approve.action_confirm()
        # ``approve_ok`` shares its compute method (``_compute_policy``)
        # with every other policy field, and that method only
        # re-triggers on ``@api.depends("policy_template_id")`` --
        # confirming already cached approve_ok=False (no approver
        # existed yet), so it must be busted explicitly before
        # Approve reads it (odoo-development-unit-test,
        # test-traps.md T-04, same fix already applied in
        # test_data_school_scholarship_disbursement.yaml).
        cls.tour_disbursement_approve.invalidate_cache()

        # Pre-Condition for 10-cancel -- a Draft disbursement, plus the
        # Cancellation Reason the wizard requires. No Line is needed:
        # cancelling a Draft document never reaches the accounting
        # hooks at all.
        (
            tour_award_cancel,
            _tour_benefit_cancel,
            _tour_funding_cancel,
            _tour_schedule_cancel,
        ) = _make_award("TOUR-DISBURSEMENT-AWARD-CANCEL-001", 500000.0)
        cls.tour_disbursement_cancel = cls.env[
            "school_scholarship_disbursement"
        ].create(
            {
                "name": "TOUR-DISBURSEMENT-CANCEL-001",
                "award_id": tour_award_cancel.id,
                "journal_id": tour_journal.id,
                "payable_account_id": tour_payable_account.id,
                "payment_method": "cash",
                "date_due": "2026-08-15",
                "user_id": admin.id,
            }
        )
        cls.env["base.cancel_reason"].create(
            {
                "name": "TOUR Disbursement Cancel Reason",
                "code": "TOURDBCR",
                # The cancel wizard's radio widget only lists reasons
                # in ir.model.all_cancel_reason_ids, which merges
                # model-specific links with every global_use=True
                # reason. Without this, the tour's radio option never
                # renders (0 matches on the trigger selector) since
                # this reason is not linked to any specific model.
                "global_use": True,
            }
        )

    def test_create(self):
        """Run the create tour for ``school_scholarship_disbursement``.

        IK: docs/school_scholarship_disbursement/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_disbursement_school_scholarship_disbursement_create",
            login="admin",
        )

    def test_confirm(self):
        """Run the confirm tour for ``school_scholarship_disbursement``.

        IK: docs/school_scholarship_disbursement/04-confirm.md
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_disbursement_school_scholarship_disbursement_confirm",
            login="admin",
        )

    def test_approve(self):
        """Run the approve tour for ``school_scholarship_disbursement``.

        IK: docs/school_scholarship_disbursement/05-approve.md
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_disbursement_school_scholarship_disbursement_approve",
            login="admin",
        )

    def test_cancel(self):
        """Run the cancel tour for ``school_scholarship_disbursement``.

        IK: docs/school_scholarship_disbursement/10-cancel.md
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_disbursement_school_scholarship_disbursement_cancel",
            login="admin",
        )
