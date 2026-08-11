# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "School Scholarship Deduction",
    "version": "14.0.1.4.1",
    "website": "https://simetri-sinergi.id",
    # pylint: disable=line-too-long
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia, Odoo Community Association (OCA)",  # noqa: B950
    # pylint: enable=line-too-long
    "contributors": [
        "Andhitia Rama <andhitia.r@gmail.com>",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": [
        "ssi_school",
        "ssi_school_scholarship",
        "ssi_customer_invoice",
        "ssi_accounting_entry_mixin",
        "ssi_company_currency_mixin",
        "web_tour",
    ],
    "data": [
        "security/res_groups/school_scholarship_deduction.xml",
        "security/ir_model_access/school_scholarship_deduction.xml",
        "security/ir_model_access/school_scholarship_deduction_line.xml",
        "security/ir_model_access/school_scholarship_deduction_allocation.xml",
        "security/ir_model_access/create_due_scholarship_deduction.xml",
        "security/ir_model_access/school_scholarship_deduction_recognition.xml",
        "security/ir_model_access/school_scholarship_deduction_recognition_line.xml",
        "security/ir_model_access/create_due_scholarship_recognition.xml",
        "security/ir_rule/school_scholarship_deduction.xml",
        "security/ir_rule/school_scholarship_deduction_recognition.xml",
        "ir_sequence/school_scholarship_deduction.xml",
        "ir_sequence/school_scholarship_deduction_recognition.xml",
        "sequence_template/school_scholarship_deduction.xml",
        "sequence_template/school_scholarship_deduction_recognition.xml",
        "approval_template/school_scholarship_deduction.xml",
        "approval_template/school_scholarship_deduction_recognition.xml",
        "policy_template/school_scholarship_deduction.xml",
        "policy_template/school_scholarship_deduction_recognition.xml",
        "menu.xml",
        "wizards/create_due_scholarship_deduction.xml",
        "wizards/create_due_scholarship_recognition.xml",
        "views/school_scholarship_deduction.xml",
        "views/school_scholarship_deduction_recognition.xml",
        "views/school_scholarship_award.xml",
        "views/customer_invoice.xml",
        "views/assets.xml",
    ],
}
