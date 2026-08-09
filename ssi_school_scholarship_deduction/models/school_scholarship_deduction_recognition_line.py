# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SchoolScholarshipDeductionRecognitionLine(models.Model):
    """
    Represents the debit/credit pair posted for one deduction Line by
    a single Recognition document.
    One record is generated per Line of the deduction being released,
    so a deduction funded by two sources produces two Recognition
    Lines carrying two different Analytic Accounts, exactly mirroring
    ``school_scholarship_deduction_line`` itself. Debit and credit
    creation is delegated to the inherited
    ``mixin.account_move_double_line`` -- a single deduction Line
    always produces exactly one balanced debit/credit pair, unlike
    the deduction document itself, whose N debit Lines are matched by
    one single credit Line at header level.
    """

    _name = "school_scholarship_deduction_recognition_line"
    _description = "School Scholarship Deduction Recognition - Line"
    _inherit = [
        "mixin.account_move_double_line",
    ]
    _order = "recognition_id, id"

    # Accounting Move Double Line Mixin (``mixin.account_move_double_line``)
    _move_id_field_name = "move_id"
    _currency_id_field_name = "currency_id"
    _debit_account_id_field_name = "debit_account_id"
    _credit_account_id_field_name = "credit_account_id"
    _debit_analytic_account_id_field_name = "analytic_account_id"
    _credit_analytic_account_id_field_name = "analytic_account_id"
    _debit_amount_currency_field_name = "amount"
    _credit_amount_currency_field_name = "amount"
    _debit_currency_id_field_name = "currency_id"
    _credit_currency_id_field_name = "currency_id"
    _debit_company_currency_id_field_name = "company_currency_id"
    _credit_company_currency_id_field_name = "company_currency_id"
    _debit_date_field_name = "date"
    _credit_date_field_name = "date"
    _debit_company_id_field_name = "company_id"
    _credit_company_id_field_name = "company_id"

    recognition_id = fields.Many2one(
        string="# Recognition",
        comodel_name="school_scholarship_deduction_recognition",
        required=True,
        ondelete="cascade",
        help="Recognition document this line belongs to.",
    )
    deduction_line_id = fields.Many2one(
        string="Deduction Line",
        comodel_name="school_scholarship_deduction_line",
        required=True,
        ondelete="restrict",
        help="Deduction Line released by this Recognition Line.",
    )
    amount = fields.Monetary(
        string="Amount",
        currency_field="company_currency_id",
        help="Portion of the Recognition document's own Amount "
        "released for this Deduction Line, already rounded to the "
        "currency's own precision.",
    )
    debit_account_id = fields.Many2one(
        string="Debit Account",
        comodel_name="account.account",
        related="deduction_line_id.final_account_id",
        help="Final Account of the Deduction Line, debited by this "
        "Recognition Line.",
    )
    credit_account_id = fields.Many2one(
        string="Credit Account",
        comodel_name="account.account",
        related="deduction_line_id.account_id",
        help="Deferred Account of the Deduction Line, credited by "
        "this Recognition Line.",
    )
    analytic_account_id = fields.Many2one(
        string="Analytic Account",
        comodel_name="account.analytic.account",
        related="deduction_line_id.analytic_account_id",
        store=True,
        help="Analytic Account of the Deduction Line's own Funding "
        "source, carried on both the debit and credit side.",
    )
    move_id = fields.Many2one(
        string="Move",
        comodel_name="account.move",
        related="recognition_id.move_id",
        help="Journal entry of the parent Recognition document.",
    )
    date = fields.Date(
        string="Date",
        related="recognition_id.date",
        help="Accounting date inherited from the parent Recognition " "document.",
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        related="recognition_id.company_id",
        help="Company inherited from the parent Recognition document.",
    )
    company_currency_id = fields.Many2one(
        string="Company Currency",
        comodel_name="res.currency",
        related="recognition_id.company_currency_id",
        help="Company currency inherited from the parent Recognition " "document.",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="recognition_id.currency_id",
        help="Currency inherited from the parent Recognition document.",
    )

    def _get_standard_label(self, direction):
        """Return the move line label, without the student's identity.

        Mirrors ``school_scholarship_deduction_line``'s own
        confidentiality-preserving label: the parent Recognition
        document's own number, combined with the Deduction Line's own
        Description -- never the student's name.

        :param direction: ``'debit'`` or ``'credit'`` (unused, both
            sides share the same label)
        :return: the composed label string
        """
        self.ensure_one()
        return "%s - %s" % (
            self.recognition_id.name,
            self.deduction_line_id.name,
        )
