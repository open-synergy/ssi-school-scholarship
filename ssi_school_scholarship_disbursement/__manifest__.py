# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "School Scholarship Disbursement",
    "version": "14.0.1.0.1",
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
        "ssi_school_scholarship",
        "ssi_accounting_entry_mixin",
        "ssi_company_currency_mixin",
        "web_tour",
    ],
    "data": [
        "security/res_groups/school_scholarship_disbursement.xml",
        "security/ir_model_access/school_scholarship_disbursement.xml",
        "security/ir_model_access/school_scholarship_disbursement_line.xml",
        "security/ir_model_access/school_scholarship_payment_link.xml",
        "security/ir_model_access/create_due_scholarship_disbursement.xml",
        "security/ir_rule/school_scholarship_disbursement.xml",
        "ir_sequence/school_scholarship_disbursement.xml",
        "sequence_template/school_scholarship_disbursement.xml",
        "approval_template/school_scholarship_disbursement.xml",
        "policy_template/school_scholarship_disbursement.xml",
        "menu.xml",
        "wizards/create_due_scholarship_disbursement.xml",
        "views/school_scholarship_disbursement.xml",
        "views/school_scholarship_award.xml",
        "views/assets.xml",
    ],
}
