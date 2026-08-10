# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
# Migration: 14.0.1.5.2 -> 14.0.1.6.0
#
# Changes: school_scholarship_award gained a new required column,
#          source_type, discriminating the billing source an award is
#          billed against (this release only registers "enrollment").
#          Odoo's own _init_column already backfills every existing
#          row with the field's default ("enrollment") as soon as the
#          column is created, before this script ever runs. This
#          script is deliberately defensive: it makes that backfill
#          explicit and auditable on a live database (25 open awards)
#          rather than relying on it having happened silently, and
#          logs how many rows it touched.

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    """Stamp ``source_type='enrollment'`` on every pre-existing award.

    Explicit and auditable stand-in for the backfill Odoo's own
    ``_init_column`` already performs silently when the column is
    created.

    :param env: the migration environment
    :param version: the version being migrated to (unused)
    :return: nothing; updates ``school_scholarship_award`` rows
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE school_scholarship_award
        SET source_type = 'enrollment'
        WHERE source_type IS NULL
        """,
    )
    _logger.info(
        "Stamped source_type='enrollment' on %s school_scholarship_award " "row(s).",
        env.cr.rowcount,
    )
