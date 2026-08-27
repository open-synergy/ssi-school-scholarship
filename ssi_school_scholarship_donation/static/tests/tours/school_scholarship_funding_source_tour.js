// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define(
    "ssi_school_scholarship_donation.school_scholarship_funding_source_tour",
    function (require) {
        "use strict";

        var tour = require("web_tour.tour");

        // IK: docs/school_scholarship_funding_source/01-create.md (E1
        // delta -- Additional Fields). Navigation (open menu -> New) is
        // taken from the base IK
        // ssi_school_scholarship/docs/school_scholarship_funding_source/
        // 01-create.md Flow steps 1-2 -- see skill
        // odoo-development-ui-test, scope-and-boundaries.md §1 ("Backing
        // dua file: tour extension = base IK ∪ delta IK"). The delta
        // assertion comes from this module's own IK: the Donation Fund
        // field is visible on the create form. The tour stops there; it
        // does not fill, save, or confirm (E1 delta-only).
        tour.register(
            "ssi_school_scholarship_donation_school_scholarship_funding_source_create",
            {
                test: true,
                url: "/web",
            },
            [
                // ── Base Flow 1 — Open the School > Configuration >
                // Scholarship > Scholarship Funding Sources menu.
                tour.stepUtils.showAppsMenuItem(),
                {
                    content: "Open the School app",
                    trigger: '.o_app[data-menu-xmlid="ssi_school.menu_school_root"]',
                },
                {
                    content: "Open the Configuration menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_school.menu_school_configuration"]',
                },
                {
                    content: "Open the Scholarship Funding Sources menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_school_scholarship.school_scholarship_funding_source_menu"]',
                },
                {
                    // Gate: wait for the TARGET action to be mounted, not
                    // just any list view (patterns.md §A).
                    content: "Scholarship Funding Sources list is displayed",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Scholarship Funding Sources)",
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

                // ── Delta assertion — the Donation Fund field is visible
                // on the create form. The tour stops here (E1
                // delta-only).
                {
                    content: "Donation Fund field is visible on the form",
                    trigger:
                        ".o_form_view.o_form_editable .o_field_widget[name='donation_fund_id']",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
            ]
        );
    }
);
