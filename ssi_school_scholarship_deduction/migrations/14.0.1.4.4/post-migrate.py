# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
# Migration: 14.0.1.4.3 -> 14.0.1.4.4
#
# Changes: school_scholarship_deduction_recognition gained its own
#          workflow/data ownership group ladder (Viewer/User/Validator,
#          Company/Company and All Child Companies/All), replacing the
#          school_scholarship_deduction_* groups it used to piggyback
#          on for every ACL, ir.rule and menu of its own. This script
#          copies each user's existing school_scholarship_deduction_*
#          membership onto the equivalent new
#          school_scholarship_deduction_recognition_* group so
#          authorization that used to come from Deduction keeps
#          working for Recognition without a manual re-grant.

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

# (old deduction group, new recognition group) pairs, one per rung of
# the workflow and data ownership ladders.
_GROUP_XMLID_PAIRS = [
    (
        "school_scholarship_deduction_viewer_group",
        "school_scholarship_deduction_recognition_viewer_group",
    ),
    (
        "school_scholarship_deduction_user_group",
        "school_scholarship_deduction_recognition_user_group",
    ),
    (
        "school_scholarship_deduction_validator_group",
        "school_scholarship_deduction_recognition_validator_group",
    ),
    (
        "school_scholarship_deduction_company_group",
        "school_scholarship_deduction_recognition_company_group",
    ),
    (
        "school_scholarship_deduction_company_child_group",
        "school_scholarship_deduction_recognition_company_child_group",
    ),
    (
        "school_scholarship_deduction_all_group",
        "school_scholarship_deduction_recognition_all_group",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    """Copy Deduction group membership onto the new Recognition groups.

    Every user already granted one of the six
    ``school_scholarship_deduction_*`` groups is added to the
    equivalent new ``school_scholarship_deduction_recognition_*``
    group introduced by this release. Runs after this module's own
    data files (including the new groups) have been loaded, so every
    XML ID resolves.

    :param env: the migration environment
    :param version: the version being migrated to (unused)
    :return: nothing; updates ``res_groups_users_rel`` rows
    """
    module = "ssi_school_scholarship_deduction"
    for deduction_xmlid, recognition_xmlid in _GROUP_XMLID_PAIRS:
        deduction_group = env.ref(
            "%s.%s" % (module, deduction_xmlid), raise_if_not_found=False
        )
        recognition_group = env.ref(
            "%s.%s" % (module, recognition_xmlid), raise_if_not_found=False
        )
        if not deduction_group or not recognition_group:
            _logger.warning(
                "Skipping %s -> %s: one of the groups was not found.",
                deduction_xmlid,
                recognition_xmlid,
            )
            continue
        openupgrade.logged_query(
            env.cr,
            """
            INSERT INTO res_groups_users_rel (gid, uid)
            SELECT %s, src.uid
            FROM res_groups_users_rel AS src
            WHERE src.gid = %s
              AND NOT EXISTS (
                  SELECT 1
                  FROM res_groups_users_rel AS dst
                  WHERE dst.gid = %s AND dst.uid = src.uid
              )
            """,
            (recognition_group.id, deduction_group.id, recognition_group.id),
        )
        _logger.info(
            "Copied %s membership onto %s (%s row(s) added).",
            deduction_xmlid,
            recognition_xmlid,
            env.cr.rowcount,
        )
