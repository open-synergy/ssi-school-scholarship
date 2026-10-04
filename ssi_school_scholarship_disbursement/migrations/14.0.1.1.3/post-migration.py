# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
# Migration: 14.0.1.1.2 -> 14.0.1.1.3
#
# Changes: opening a Disbursement now fills ``amount_realized`` on every
#          Schedule line it realizes. Documents opened before this
#          version left it at zero, so this script backfills it from
#          the Disbursement lines of every Open/Done document.

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Backfill ``amount_realized`` on already realized Schedule lines.

    Sets each Schedule line's ``amount_realized`` to the sum of
    ``price_subtotal`` over all lines of the Open/Done Disbursement
    documents that point at it.

    :param env: the Odoo environment
    :param version: the previously installed module version
    :return: nothing
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE school_scholarship_award_schedule schedule
        SET amount_realized = totals.amount
        FROM (
            SELECT line.schedule_id AS schedule_id,
                SUM(line.price_subtotal) AS amount
            FROM school_scholarship_disbursement_line line
            JOIN school_scholarship_disbursement disbursement
                ON disbursement.id = line.disbursement_id
            WHERE disbursement.state IN ('open', 'done')
                AND line.schedule_id IS NOT NULL
            GROUP BY line.schedule_id
        ) totals
        WHERE schedule.id = totals.schedule_id
            AND schedule.disbursement_id IS NOT NULL
        """,
    )
