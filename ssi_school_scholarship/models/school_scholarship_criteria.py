# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolScholarshipCriteria(models.Model):
    """
    Represents one eligibility criterion checklist item of a scholarship
    program.
    A criterion may be checked manually by the committee, derived from a
    search domain, or evaluated by a snippet of Python code through the
    ``mixin.localdict`` safe-eval context. It only records the rule
    itself, not its automated evaluation: scoring and
    auto-disqualification are a later, application-layer item.
    """

    _name = "school_scholarship_criteria"
    _inherit = ["mixin.localdict"]
    _description = "School Scholarship Criteria"
    _order = "sequence, id"

    _DEFAULT_PYTHON_CODE = """# Available variables:
#  - env: Odoo Environment on which the code is evaluated.
#  - document: school_scholarship_criteria record.
#  - result: set to True if the criterion is met, False otherwise.
result = True"""

    program_id = fields.Many2one(
        string="Program",
        comodel_name="school_scholarship_program",
        required=True,
        ondelete="cascade",
        help="Scholarship program this criterion belongs to.",
    )
    name = fields.Char(
        string="Criteria",
        required=True,
        help="Short description of this eligibility criterion, shown "
        "to the committee as a checklist item.",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=5,
        help="Display order of this criterion within the program.",
    )
    evaluation_method = fields.Selection(
        string="Evaluation Method",
        selection=[
            ("manual", "Manual"),
            ("domain", "Domain"),
            ("python", "Python Code"),
        ],
        default="manual",
        required=True,
        help="How this criterion is evaluated: checked manually by "
        "the committee, derived from a search Domain, or evaluated "
        "by a Python Code snippet.",
    )
    criteria_domain = fields.Char(
        string="Domain",
        help="Search domain evaluated against the applicant. "
        "Required when Evaluation Method is Domain.",
    )
    python_code = fields.Text(
        string="Python Code",
        default=_DEFAULT_PYTHON_CODE,
        help="Python code evaluated in the ``mixin.localdict`` "
        "context. Must assign a boolean to result. Required when "
        "Evaluation Method is Python Code.",
    )
    is_hard_requirement = fields.Boolean(
        string="Is Hard Requirement",
        default=False,
        help="Check this if failing this criterion disqualifies the "
        "applicant outright, rather than merely lowering their "
        "score.",
    )
    weight = fields.Float(
        string="Weight",
        default=0.0,
        help="Relative weight of this criterion in the committee's " "scoring.",
    )

    @api.constrains("evaluation_method", "criteria_domain")
    def _check_domain_required(self):
        """Require ``criteria_domain`` when evaluated by Domain.

        :raises ValidationError: when ``evaluation_method`` is
            ``domain`` and ``criteria_domain`` is empty.
        """
        for record in self:
            if record.evaluation_method == "domain" and not record.criteria_domain:
                error_message = """
Document Type: %s
Context: Configure criteria evaluation
Database ID: %s
Problem: Evaluation Method Domain requires Domain to be filled in
Solution: Enter a Domain, or change Evaluation Method
""" % (
                    self._description,
                    record.id,
                )
                raise ValidationError(_(error_message))

    @api.constrains("evaluation_method", "python_code")
    def _check_python_code_required(self):
        """Require ``python_code`` when evaluated by Python Code.

        :raises ValidationError: when ``evaluation_method`` is
            ``python`` and ``python_code`` is empty.
        """
        for record in self:
            if record.evaluation_method == "python" and not record.python_code:
                error_message = """
Document Type: %s
Context: Configure criteria evaluation
Database ID: %s
Problem: Evaluation Method Python Code requires Python Code to be filled in
Solution: Enter Python Code, or change Evaluation Method
""" % (
                    self._description,
                    record.id,
                )
                raise ValidationError(_(error_message))
