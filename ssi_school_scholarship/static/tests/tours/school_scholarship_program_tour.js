// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define("ssi_school_scholarship.school_scholarship_program_tour", function (
    require
) {
    "use strict";

    var tour = require("web_tour.tour");

    // IK: docs/school_scholarship_program/01-create.md
    tour.register(
        "ssi_school_scholarship_school_scholarship_program_create",
        {
            test: true,
            url: "/web",
        },
        [
            // ── Flow 1 — Open the School > Scholarship > Configuration >
            // Scholarship Programs menu. "Configuration"
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
                content: "Open the Scholarship Programs menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_school_scholarship.school_scholarship_program_menu"]',
            },
            {
                // Gerbang: tunggu action TUJUAN benar-benar terpasang --
                // bukan sekadar "ada list di layar" (patterns.md §A).
                content: "Scholarship Programs list is displayed",
                trigger:
                    ".o_control_panel .breadcrumb-item.active:contains(Scholarship Programs)",
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
            // Scholarship Type (selecting it triggers the onchange that
            // fills the Deduction/Disbursement/Deferred Recognition tabs),
            // School, Academic Year. Funding Basis keeps its "Need Based"
            // default. Code is left as "/" so Flow 7 (Generate Code) has
            // an effect.
            {
                content: "Fill in the Name",
                trigger: ".o_field_widget[name='name']",
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text TOUR Program Create",
            },
            {
                content: "Fill in the Code",
                trigger: ".o_field_widget[name='code']",
                run: "text /",
            },
            {
                content: "Select the Scholarship Type",
                trigger: ".o_field_many2one[name='type_id'] input",
                run: "text TOUR Program Scholarship Type",
            },
            {
                content: "Pick the Scholarship Type from the dropdown",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR Program Scholarship Type)",
                in_modal: false,
            },
            {
                // Gerbang: tunggu onchange(type_id) selesai mengisi field
                // akun sebelum melanjutkan -- baru SESUDAH type_id
                // terpilih field ini bisa berisi teks.
                content: "Deduction Journal is filled by the onchange",
                trigger:
                    ".o_field_many2one[name='deduction_journal_id'] input:not([value=''])",
                run: function () {
                    // Assertion only; do not trigger the default click.
                },
            },
            {
                content: "Select the School",
                trigger: ".o_field_many2one[name='school_id'] input",
                run: "text TOUR Program School",
            },
            {
                content: "Pick the School from the dropdown",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR Program School)",
                in_modal: false,
            },
            {
                content: "Select the Academic Year",
                trigger: ".o_field_many2one[name='academic_year_id'] input",
                run: "text TOUR Program Academic Year",
            },
            {
                content: "Pick the Academic Year from the dropdown",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR Program Academic Year)",
                in_modal: false,
            },

            // ── Flow 4 — On the Eligibility tab, select the Funding
            // Sources (required). Grades, Quota, Is Renewable and Max
            // Renewal keep their defaults.
            {
                content: "Open the Eligibility tab",
                trigger: ".o_notebook .nav-link:contains(Eligibility)",
            },
            {
                content: "Open the Funding Sources tag input",
                trigger: ".o_field_many2many_tags[name='funding_source_ids'] input",
                run: "text TOUR Program Funding Source",
            },
            {
                content: "Pick the Funding Source from the dropdown",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR Program Funding Source)",
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
                    // Assertion only; do not trigger the default click.
                },
            },

            // ── Flow 8 — Click Save.
            {
                content: "Save the record",
                trigger: ".o_form_button_save",
            },

            // ── Post-Condition — a new Scholarship Program record is
            // created and active.
            {
                content: "Record is saved",
                trigger:
                    ".o_control_panel .breadcrumb-item.active:contains(TOUR Program Create)",
                extra_trigger: ".o_form_view.o_form_readonly",
                run: function () {
                    // Assertion only; do not trigger the default click.
                },
            },
        ]
    );
});
