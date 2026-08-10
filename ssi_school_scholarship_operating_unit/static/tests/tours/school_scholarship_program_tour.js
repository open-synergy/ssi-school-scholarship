// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define(
    "ssi_school_scholarship_operating_unit.school_scholarship_program_tour",
    function (require) {
        "use strict";

        var tour = require("web_tour.tour");

        // IK: docs/school_scholarship_program/01-create.md (E1 delta --
        // Additional Fields). Navigation (open menu -> New) is taken from
        // the base IK
        // ssi_school_scholarship/docs/school_scholarship_program/
        // 01-create.md Flow steps 1-2 -- see skill
        // odoo-development-ui-test, scope-and-boundaries.md §1 ("Backing
        // dua file: tour extension = base IK ∪ delta IK"). The delta
        // assertion comes from this module's own IK: the Operating Unit
        // field is visible on the create form for a user in the
        // operating_unit.group_multi_operating_unit group. The tour stops
        // there; it does not fill, save, or confirm (E1 delta-only).
        tour.register(
            "ssi_school_scholarship_operating_unit_school_scholarship_program_create",
            {
                test: true,
                url: "/web",
            },
            [
                // ── Base Flow 1 — Open the School > Scholarship >
                // Configuration > Scholarship Programs menu.
                tour.stepUtils.showAppsMenuItem(),
                {
                    content: "Open the School app",
                    trigger: '.o_app[data-menu-xmlid="ssi_school.menu_school_root"]',
                },
                {
                    content: "Open the Scholarship menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_school_scholarship.menu_school_scholarship"]',
                },
                {
                    content: "Open the Scholarship Programs menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_school_scholarship.school_scholarship_program_menu"]',
                },
                {
                    // Gate: wait for the TARGET action to be mounted, not
                    // just any list view (patterns.md §A).
                    content: "Scholarship Programs list is displayed",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Scholarship Programs)",
                    extra_trigger: ".o_list_view",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },

                // ── Base Flow 2 — Click the New button. (14.0: "Create")
                {
                    content: "Click New",
                    trigger: ".o_list_button_add",
                    extra_trigger: ".o_list_view",
                },
                {
                    content: "Form is open in edit mode",
                    trigger: ".o_form_view.o_form_editable",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },

                // ── Delta assertion — the Operating Unit field is visible
                // on the create form for a user in the multi operating
                // unit group. The tour stops here (E1 delta-only).
                {
                    content: "Operating Unit field is visible on the form",
                    trigger:
                        ".o_form_view.o_form_editable .o_field_widget[name='operating_unit_ids']",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
            ]
        );
    }
);
