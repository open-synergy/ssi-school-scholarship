# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase -- NOT HttpCase. In 14.0, HttpCase does not set up
# cls.env in setUpClass, so fixtures written there would fail with
# AttributeError before the browser even starts.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiSchoolScholarshipDeductionRecognition(HttpSavepointCase):
    """Tour tests for the
    ``school_scholarship_deduction_recognition`` work instructions.
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
                "name": "TOUR Recognition Grade Type",
                "code": "TOURRCGT",
            }
        )
        tour_school = cls.env["school"].create(
            {
                "name": "TOUR Recognition School",
                "code": "TOURRCS",
                "grade_type_id": tour_grade_type.id,
            }
        )
        tour_academic_year = cls.env["school_academic_year"].create(
            {
                "name": "TOUR Recognition Academic Year",
                "code": "TOURRCY",
                "date_start": "2026-07-01",
                "date_end": "2027-06-30",
            }
        )
        tour_academic_term = cls.env["school_academic_term"].create(
            {
                "name": "TOUR Recognition Academic Term",
                "code": "TOURRCTM",
                "date_start": "2026-07-01",
                "date_end": "2026-12-31",
                "year_id": tour_academic_year.id,
            }
        )
        tour_grade = cls.env["school_grade"].create(
            {
                "name": "TOUR Recognition Grade",
                "code": "TOURRCG",
                "type_id": tour_grade_type.id,
            }
        )
        tour_grade_class = cls.env["school_grade_class"].create(
            {
                "name": "TOUR Recognition Grade Class",
                "code": "TOURRCGC",
                "school_id": tour_school.id,
                "grade_id": tour_grade.id,
            }
        )
        tour_contact = cls.env["res.partner"].create(
            {
                "name": "TOUR Recognition Student Contact",
            }
        )
        tour_student = cls.env["school_student"].create(
            {
                "name": "TOUR Recognition Student",
                "code": "TOURRCST",
                "contact_id": tour_contact.id,
                "school_id": tour_school.id,
            }
        )
        tour_enrollment = cls.env["school_enrollment"].create(
            {
                "name": "TOUR-RECOGNITION-ENR-001",
                "academic_year_id": tour_academic_year.id,
                "academic_term_id": tour_academic_term.id,
                "school_id": tour_school.id,
                "grade_id": tour_grade.id,
                "grade_class_id": tour_grade_class.id,
                "student_id": tour_student.id,
            }
        )

        # Pre-Condition -- a Funding Source, a Product, a Program with
        # one Scope line (Allow Asymmetric Recognition enabled, since
        # these tours exercise the deferred-recognition accounting
        # entry itself, not the symmetry guard), and the account/
        # journal trio a deferred Award needs.
        tour_analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "TOUR Recognition Analytic",
            }
        )
        tour_funding_source = cls.env["school_scholarship_funding_source"].create(
            {
                "name": "TOUR Recognition Funding Source",
                "code": "TOURRCF",
                "analytic_account_id": tour_analytic_account.id,
            }
        )
        tour_product = cls.env["product.product"].create(
            {
                "name": "TOUR Recognition Product",
                "type": "service",
            }
        )
        tour_journal = cls.env["account.journal"].create(
            {
                "name": "TOUR Recognition Sale Journal",
                "code": "TRCJ",
                "type": "sale",
            }
        )
        tour_receivable_account = cls.env["account.account"].create(
            {
                "name": "TOUR Recognition Receivable Account",
                "code": "TOURRCRA",
                "user_type_id": account_type_receivable.id,
                "reconcile": True,
            }
        )
        tour_discount_account = cls.env["account.account"].create(
            {
                "name": "TOUR Recognition Discount Account",
                "code": "TOURRCDA",
                "user_type_id": account_type_income.id,
                "reconcile": False,
            }
        )
        tour_deferred_account = cls.env["account.account"].create(
            {
                "name": "TOUR Recognition Deferred Account",
                "code": "TOURRCFA",
                "user_type_id": account_type_asset.id,
                "reconcile": False,
            }
        )
        tour_type = cls.env["school_scholarship_type"].create(
            {
                "name": "TOUR Recognition Scholarship Type",
                "code": "TOURRCTY",
                "deduction_journal_id": tour_journal.id,
                "discount_account_id": tour_discount_account.id,
            }
        )
        tour_program = cls.env["school_scholarship_program"].create(
            {
                "name": "TOUR Recognition Program",
                "code": "TOURRCPRG",
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
                    "expense_account_id": tour_discount_account.id,
                    "deferred_discount_account_id": tour_deferred_account.id,
                    "recognition_journal_id": tour_journal.id,
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

        def _make_deduction(name, award, funding, schedule, amount):
            """Build a Deduction that defers automatically at create time.

            ``date`` (2026-03-01) is deliberately earlier than the
            Award's own Start Date (2026-07-01), so
            ``recognition_method`` computes to ``deferred`` -- and
            ``deferred_account_id``/``recognition_journal_id`` are set
            explicitly here rather than left to
            ``onchange_deferred_account_id``/
            ``onchange_recognition_journal_id``, since a plain
            ``create()`` call never runs a form's own onchange chain.

            :param name: unique name assigned to the Deduction
            :param award: the ``school_scholarship_award`` this
                Deduction realizes
            :param funding: the Award's own Funding line
            :param schedule: the Award's own Schedule line
            :param amount: the Deduction Line's own Price Unit, also
                the resulting Deduction's own Amount Total
            :return: the created ``school_scholarship_deduction``
                record
            """
            return cls.env["school_scholarship_deduction"].create(
                {
                    "name": name,
                    "award_id": award.id,
                    "date": "2026-03-01",
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
                                "schedule_id": schedule.id,
                                "funding_id": funding.id,
                                "final_account_id": tour_discount_account.id,
                                "name": "%s Line" % name,
                                "uom_quantity": 1,
                                "price_unit": amount,
                            },
                        )
                    ],
                }
            )

        # Pre-Condition for 01-create -- a deferred Deduction with no
        # Recognition yet, so the tour has something to select.
        (
            tour_award_create,
            _tour_benefit_create,
            tour_funding_create,
            tour_schedule_create,
        ) = _make_award("TOUR-RECOGNITION-AWARD-CREATE-001", 400000.0)
        _make_deduction(
            "TOUR-RECOGNITION-DEDUCTION-CREATE-001",
            tour_award_create,
            tour_funding_create,
            tour_schedule_create,
            400000.0,
        )

        # Pre-Condition for 05-approve -- a Recognition document
        # already pushed to Waiting for Approval in Python via
        # ``action_confirm()``, since Confirm itself has no tour of
        # its own in this item.
        (
            tour_award_approve,
            _tour_benefit_approve,
            tour_funding_approve,
            tour_schedule_approve,
        ) = _make_award("TOUR-RECOGNITION-AWARD-APPROVE-001", 400000.0)
        tour_deduction_approve = _make_deduction(
            "TOUR-RECOGNITION-DEDUCTION-APPROVE-001",
            tour_award_approve,
            tour_funding_approve,
            tour_schedule_approve,
            400000.0,
        )
        cls.tour_recognition_approve = cls.env[
            "school_scholarship_deduction_recognition"
        ].create(
            {
                "name": "TOUR-RECOGNITION-APPROVE-001",
                "deduction_id": tour_deduction_approve.id,
                "date": "2026-08-01",
                "journal_id": tour_journal.id,
                "amount": 400000.0,
                "user_id": admin.id,
            }
        )
        cls.tour_recognition_approve.action_confirm()
        # ``approve_ok`` shares its compute method (``_compute_policy``)
        # with every other policy field, and that method only
        # re-triggers on ``@api.depends("policy_template_id")`` --
        # confirming already cached approve_ok=False (no approver
        # existed yet), so it must be busted explicitly before
        # Approve reads it (odoo-development-unit-test,
        # test-traps.md T-04, same fix already applied in
        # test_data_school_scholarship_deduction.yaml).
        cls.tour_recognition_approve.invalidate_cache()

    def test_create(self):
        """Run the create tour for ``school_scholarship_deduction_recognition``.

        IK: docs/school_scholarship_deduction_recognition/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_deduction_school_scholarship_deduction_recognition_create",
            login="admin",
        )

    def test_approve(self):
        """Run the approve tour for ``school_scholarship_deduction_recognition``.

        IK: docs/school_scholarship_deduction_recognition/05-approve.md
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_deduction_school_scholarship_deduction_recognition_approve",
            login="admin",
        )
