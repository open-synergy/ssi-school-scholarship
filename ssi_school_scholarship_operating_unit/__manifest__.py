# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "School Scholarship - Operating Unit",
    "version": "14.0.1.0.1",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia, "
    "Odoo Community Association (OCA)",
    "contributors": [
        "Andhitia Rama <andhitia.r@gmail.com>",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": [
        "ssi_school_scholarship",
        "ssi_school_operating_unit",
        "ssi_operating_unit_mixin",
        "web_tour",
    ],
    "data": [
        "security/res_groups/school_scholarship_award.xml",
        "security/ir_rule/school_scholarship_type.xml",
        "security/ir_rule/school_scholarship_funding_source.xml",
        "security/ir_rule/school_scholarship_program.xml",
        "security/ir_rule/school_scholarship_award.xml",
        "views/school_scholarship_type.xml",
        "views/school_scholarship_funding_source.xml",
        "views/school_scholarship_program.xml",
        "views/school_scholarship_award.xml",
        "views/assets.xml",
    ],
    "demo": [],
}
