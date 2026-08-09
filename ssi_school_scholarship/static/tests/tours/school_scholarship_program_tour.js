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
            // fills the Deduction/Disbursement/Deferred Recognition tabs
            // in the background -- those tabs are reviewed later, in
            // Flow 7, once they are actually open), School, Academic
            // Year. Funding Basis keeps its "Need Based" default. Code is
            // left as "/" so Flow 8 (Generate Code) has an effect.
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
                // Class CSS widget many2many_tags legacy 14.0 adalah
                // "o_field_many2manytags" -- TANPA underscore antara
                // "many2many" dan "tags" (lihat FieldMany2ManyTags.
                // className di web/static/src/js/fields/
                // relational_fields.js). Selector sebelumnya
                // ".o_field_many2many_tags" (dengan underscore) tidak
                // pernah cocok.
                content: "Open the Funding Sources tag input",
                trigger: ".o_field_many2manytags[name='funding_source_ids'] input",
                run: "text TOUR Program Funding Source",
            },
            {
                content: "Pick the Funding Source from the dropdown",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR Program Funding Source)",
                in_modal: false,
            },

            // ── Flow 5 — On the Scope tab, add one line. The program is
            // rejected on save without at least one Scope line, so this
            // step is required, not optional. Scope Basis, Benefit Type,
            // Computation and Periodicity keep their defaults (Product /
            // Fee Reduction / Percentage / Per Payment Term); only
            // Product and Percentage need to be filled in, since
            // Percentage defaults to 0 which the Percentage computation
            // rejects.
            {
                content: "Open the Scope tab",
                trigger: ".o_notebook .nav-link:contains(Scope)",
            },
            {
                content: "Add a Scope line",
                trigger:
                    ".o_field_widget[name='scope_ids'] .o_field_x2many_list_row_add a",
            },
            {
                content: "Select the Product",
                trigger: ".o_selected_row .o_field_widget[name='product_id'] input",
                run: "text TOUR Program Product",
            },
            {
                content: "Pick the Product from the dropdown",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR Program Product)",
                in_modal: false,
            },
            {
                // Plain Float fields in a 14.0 editable list render as a
                // bare `<input class="o_field_widget o_input" name=
                // "percentage">` -- unlike Many2one/Monetary, there is no
                // wrapping element carrying the `name=` attribute
                // separately from the `<input>` itself, so the selector
                // must target the input directly rather than looking for
                // an `input` descendant of `.o_field_widget[name=...]`.
                content: "Fill in the Percentage",
                trigger: ".o_selected_row input[name='percentage']",
                run: "text 40",
            },
            {
                // Commit the last edited cell -- never `press Tab`
                // (odoo-development-ui-test references/patterns.md §C).
                // Click an already-committed cell on the same row to
                // blur.
                content: "Commit the Scope line",
                trigger: ".o_selected_row .o_field_widget[name='product_id']",
                run: "click",
            },

            // ── Flow 7 — Review the accounting fields defaulted from the
            // Scholarship Type on the Deduction tab. Opening the tab is
            // required before its fields can be asserted: they are
            // rendered inside a Bootstrap `.tab-pane` that Odoo keeps
            // `display:none` while a different tab (Eligibility, the
            // notebook's first page and therefore the default active one)
            // is selected, so `.o_external_button` never becomes
            // `:visible` -- and jQuery/Sizzle never marks a hidden
            // ancestor's descendant as visible -- until this tab is
            // opened, no matter how long the onchange RPC (fired back in
            // Flow 3 when the type was selected) has already completed.
            {
                content: "Open the Deduction tab",
                trigger: ".o_notebook .nav-link:contains(Deduction)",
            },
            {
                // Gerbang: `.o_external_button` (tombol "buka record
                // terkait") hanya dirender oleh widget many2one setelah
                // field benar-benar berisi nilai -- Sizzle membaca
                // atribut `value=` pada <input> lewat `defaultValue`
                // (nilai HTML awal), bukan `.value` JS yang diisi
                // onchange, jadi `input:not([value=''])` tidak pernah
                // cocok (lihat odoo-development-ui-test
                // references/patterns.md §L).
                content: "Deduction Journal is filled by the onchange",
                trigger:
                    ".o_field_many2one[name='deduction_journal_id'] .o_external_button",
                run: function () {
                    // Assertion only; do not trigger the default click.
                },
            },

            // ── Flow 8 — Click Generate Code in the header to
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

            // ── Flow 9 — Click Save.
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
