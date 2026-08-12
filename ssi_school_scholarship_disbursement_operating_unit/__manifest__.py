# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "School Scholarship Disbursement - Operating Unit",
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
        "ssi_school_scholarship_disbursement",
        "ssi_school_scholarship_operating_unit",
        "ssi_financial_accounting_operating_unit",
        "web_tour",
    ],
    "data": [
        "security/res_groups/school_scholarship_disbursement.xml",
        "security/ir_rule/school_scholarship_disbursement.xml",
        "views/school_scholarship_disbursement.xml",
        "views/assets.xml",
    ],
    "demo": [],
}
