// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define(
    "ssi_school_scholarship.school_scholarship_funding_source_tour",
    function (require) {
        "use strict";

        var tour = require("web_tour.tour");

        // IK: docs/school_scholarship_funding_source/01-create.md
        tour.register(
            "ssi_school_scholarship_school_scholarship_funding_source_create",
            {
                test: true,
                url: "/web",
            },
            [
                // ── Flow 1 — Open the School > Scholarship > Configuration >
                // Scholarship Funding Sources menu. "Configuration"
                // (menu_school_scholarship_configuration) is a level-3
                // grouping menuitem with no action= attribute, so 14.0
                // renders it as a non-clickable dropdown header without
                // data-menu-xmlid -- there is no step for it (patterns.md
                // skill odoo-development-ui-test §A).
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
                    content: "Open the Scholarship Funding Sources menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_school_scholarship.school_scholarship_funding_source_menu"]',
                },
                {
                    // Gerbang: tunggu action TUJUAN benar-benar terpasang --
                    // bukan sekadar "ada list di layar" (patterns.md §A).
                    content: "Scholarship Funding Sources list is displayed",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Scholarship Funding Sources)",
                    extra_trigger: ".o_list_view",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },

                // ── Flow 2 — Click the New button. (14.0: "Create")
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

                // ── Flow 3 — Fill in the required fields: Name, Code,
                // Analytic Account. Code is left as "/" so Flow 6
                // (Generate Code) has an effect.
                {
                    content: "Fill in the Name",
                    trigger: ".o_field_widget[name='name']",
                    extra_trigger: ".o_form_view.o_form_editable",
                    run: "text TOUR Funding Source Create",
                },
                {
                    content: "Fill in the Code",
                    trigger: ".o_field_widget[name='code']",
                    run: "text /",
                },
                {
                    content: "Select the Analytic Account",
                    trigger: ".o_field_many2one[name='analytic_account_id'] input",
                    run: "text TOUR Funding Source Analytic",
                },
                {
                    content: "Pick the Analytic Account from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR Funding Source Analytic)",
                    in_modal: false,
                },

                // ── Flow 6 — Click Generate Code in the header to
                // automatically assign a code from the configured
                // sequence.template, since the Code field is still "/".
                {
                    content: "Click Generate Code",
                    trigger:
                        ".o_statusbar_buttons button[name='action_generate_code']",
                    extra_trigger: ".o_form_view.o_form_editable",
                },
                {
                    content: "Record is saved by Generate Code",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:not(:contains(New))",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },

                // ── Flow 7 — Click Save.
                {
                    content: "Save the record",
                    trigger: ".o_form_button_save",
                },

                // ── Post-Condition — a new Scholarship Funding Source
                // record is created and active.
                {
                    content: "Record is saved",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(TOUR Funding Source Create)",
                    extra_trigger: ".o_form_view.o_form_readonly",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
            ]
        );
    }
);
