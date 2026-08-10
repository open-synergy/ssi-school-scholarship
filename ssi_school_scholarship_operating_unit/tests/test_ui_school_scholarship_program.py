# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiSchoolScholarshipProgram(HttpSavepointCase):
    """Tour test for the Operating Unit field on
    ``school_scholarship_program`` create.
    """

    def setUp(self):
        """Grant ``admin`` the multi operating unit group.

        Pre-Condition IK: the Operating Unit field is gated by
        ``groups="operating_unit.group_multi_operating_unit"`` in the
        form view -- without membership, the field is never rendered
        and the delta assertion would never find it. ``HttpSavepointCase``
        is required in 14.0 (``HttpCase`` there does not set up
        ``cls.env`` in ``setUpClass``); this fixture only needs
        ``self.env``, so overriding instance ``setUp`` (rather than
        ``setUpClass``) is enough.
        """
        super().setUp()
        self.user_admin = self.env.ref("base.user_admin")
        self.env.ref("operating_unit.group_multi_operating_unit").sudo().write(
            {"users": [(4, self.user_admin.id)]}
        )

    def test_create(self):
        """Run the create tour for ``school_scholarship_program``.

        IK: docs/school_scholarship_program/01-create.md (E1 delta --
        Additional Fields)
        """
        self.start_tour(
            "/web",
            "ssi_school_scholarship_operating_unit_school_scholarship_program_create",
            login="admin",
        )
