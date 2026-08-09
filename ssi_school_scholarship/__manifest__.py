# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "School Scholarship",
    "version": "14.0.1.1.0",
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
        "ssi_master_data_mixin",
        "ssi_financial_accounting",
        "ssi_m2o_configurator_mixin",
        "web_tour",
    ],
    "data": [
        "security/ir_module_category_data.xml",
        "security/res_groups/school_scholarship_type.xml",
        "security/res_groups/school_scholarship_funding_source.xml",
        "security/res_groups/school_scholarship_program.xml",
        "security/ir_model_access/school_scholarship_type.xml",
        "security/ir_model_access/school_scholarship_funding_source.xml",
        "security/ir_model_access/school_scholarship_program.xml",
        "security/ir_model_access/school_scholarship_program_scope.xml",
        "security/ir_model_access/school_scholarship_criteria.xml",
        "menu.xml",
        "views/school_scholarship_type.xml",
        "views/school_scholarship_funding_source.xml",
        "views/school_scholarship_program.xml",
        "views/assets.xml",
    ],
}
