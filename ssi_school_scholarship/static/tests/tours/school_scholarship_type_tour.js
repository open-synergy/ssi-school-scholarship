// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define("ssi_school_scholarship.school_scholarship_type_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    // IK: docs/school_scholarship_type/01-create.md
    tour.register(
        "ssi_school_scholarship_school_scholarship_type_create",
        {
            test: true,
            url: "/web",
        },
        [
            // ── Flow 1 — Open the School > Scholarship > Configuration >
            // Scholarship Types menu. "Configuration"
            // (menu_school_scholarship_configuration) is a level-3 grouping
            // menuitem with no action= attribute, so 14.0 renders it as a
            // non-clickable dropdown header without data-menu-xmlid --
            // there is no step for it (patterns.md skill
            // odoo-development-ui-test §A).
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
                content: "Open the Scholarship Types menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_school_scholarship.school_scholarship_type_menu"]',
            },
            {
                // Gerbang: tunggu action TUJUAN benar-benar terpasang --
                // bukan sekadar "ada list di layar" (patterns.md §A).
                content: "Scholarship Types list is displayed",
                trigger:
                    ".o_control_panel .breadcrumb-item.active:contains(Scholarship Types)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
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
                    // Assertion only; do not trigger the default click action.
                },
            },

            // ── Flow 3 — Fill in the required fields: Name, Code.
            // Sequence is defaulted to 5, so it is not touched here. Code
            // is left as "/" so Flow 7 (Generate Code) has an effect.
            {
                content: "Fill in the Name",
                trigger: ".o_field_widget[name='name']",
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text TOUR Scholarship Type Create",
            },
            {
                content: "Fill in the Code",
                trigger: ".o_field_widget[name='code']",
                run: "text /",
            },

            // ── Flow 4 — On the Deduction tab, fill in Deduction Journal
            // and Discount Account (both required). Is Employee Benefit
            // is left unchecked -- Employee Benefit Account and Deduction
            // Product are optional and are not needed to save the record.
            {
                content: "Open the Deduction tab",
                trigger: ".o_notebook .nav-link:contains(Deduction)",
            },
            {
                content: "Select the Deduction Journal",
                trigger: ".o_field_many2one[name='deduction_journal_id'] input",
                run: "text TOUR Scholarship Sale Journal",
            },
            {
                content: "Pick the Deduction Journal from the dropdown",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR Scholarship Sale Journal)",
                in_modal: false,
            },
            {
                content: "Select the Discount Account",
                trigger: ".o_field_many2one[name='discount_account_id'] input",
                run: "text TOUR Scholarship Discount Account",
            },
            {
                content: "Pick the Discount Account from the dropdown",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR Scholarship Discount Account)",
                in_modal: false,
            },

            // ── Flow 7 — Click Generate Code in the header to
            // automatically assign a code from the configured
            // sequence.template, since the Code field is still "/".
            {
                content: "Click Generate Code",
                trigger: ".o_statusbar_buttons button[name='action_generate_code']",
                extra_trigger: ".o_form_view.o_form_editable",
            },
            {
                content: "Record is saved by Generate Code",
                trigger: ".o_control_panel .breadcrumb-item.active:not(:contains(New))",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // ── Flow 8 — Click Save.
            {
                content: "Save the record",
                trigger: ".o_form_button_save",
            },

            // ── Post-Condition — a new Scholarship Type record is created
            // and active.
            {
                content: "Record is saved",
                trigger:
                    ".o_control_panel .breadcrumb-item.active:contains(TOUR Scholarship Type Create)",
                extra_trigger: ".o_form_view.o_form_readonly",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ]
    );
});
