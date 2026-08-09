// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define(
    "ssi_school_scholarship_deduction.school_scholarship_deduction_recognition_tour",
    function (require) {
        "use strict";

        var tour = require("web_tour.tour");

        // Shared navigation block, reused verbatim by every tour below --
        // Flow step 1 of every IK in
        // docs/school_scholarship_deduction_recognition/: "Open the
        // School > Scholarship > Scholarship Deduction Recognitions
        // menu."
        function openScholarshipDeductionRecognitionsList() {
            return [
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
                    content: "Open the Scholarship Deduction Recognitions menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_school_scholarship_deduction.school_scholarship_deduction_recognition_menu"]',
                },
                {
                    // Gate: wait for the Scholarship Deduction
                    // Recognitions action to actually be mounted, not
                    // just any list view left over from the landing
                    // action (odoo-development-ui-test
                    // references/patterns.md §A).
                    content: "Scholarship Deduction Recognitions list is displayed",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Scholarship Deduction Recognitions)",
                    extra_trigger: ".o_list_view",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
            ];
        }

        // IK: docs/school_scholarship_deduction_recognition/01-create.md
        tour.register(
            "ssi_school_scholarship_deduction_school_scholarship_deduction_recognition_create",
            {
                test: true,
                url: "/web",
            },
            [].concat(openScholarshipDeductionRecognitionsList(), [
                // Flow 2 — Click the New button. (14.0: "Create")
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

                // ── Flow 3 — Select Deduction; Journal and Amount are
                // both filled by its own onchange.
                {
                    content: "Select the Deduction",
                    trigger: ".o_field_many2one[name='deduction_id'] input",
                    run: "text TOUR-RECOGNITION-DEDUCTION-CREATE-001",
                },
                {
                    content: "Pick the Deduction from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR-RECOGNITION-DEDUCTION-CREATE-001)",
                    in_modal: false,
                },
                {
                    // Gate: wait for the Deduction onchange's RPC to
                    // fill Journal before saving. `.o_external_button`
                    // (the "open related record" button) is only
                    // rendered by the many2one widget once the field
                    // actually holds a value -- Sizzle reads an
                    // `input[value=...]` attribute selector via
                    // `defaultValue` (the initial HTML value), not the
                    // live `.value` JS property an `@api.onchange`
                    // fills at runtime, so that selector never matches
                    // (odoo-development-ui-test references/patterns.md
                    // §L; same fix as
                    // ssi_school_scholarship_program_tour.js commit
                    // b73daad).
                    content: "Journal reflects the Deduction onchange before saving",
                    trigger: ".o_field_many2one[name='journal_id'] .o_external_button",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },

                // ── Flow 4 — Click Save.
                {
                    content: "Save the record",
                    trigger: ".o_form_button_save",
                },

                // ── Post-Condition — a new Recognition record is
                // created in Draft status.
                {
                    content: "Record is saved",
                    trigger: ".o_form_view.o_form_readonly",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
                {
                    content: "Status is Draft",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='draft'].btn-primary",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
            ])
        );

        // IK: docs/school_scholarship_deduction_recognition/05-approve.md
        tour.register(
            "ssi_school_scholarship_deduction_school_scholarship_deduction_recognition_approve",
            {
                test: true,
                url: "/web",
            },
            [].concat(openScholarshipDeductionRecognitionsList(), [
                // Flow 2 — Open the record to approve.
                {
                    content: "Open the record",
                    trigger:
                        ".o_data_row:contains(TOUR-RECOGNITION-APPROVE-001) .o_data_cell:first",
                },
                {
                    content: "Form is open",
                    trigger: ".o_form_view",
                    extra_trigger: ".o_form_view.o_form_readonly",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },

                // Flow 3 — Click the Approve button.
                {
                    content: "Click the Approve button",
                    trigger:
                        ".o_statusbar_buttons button[name='action_approve_approval']",
                    extra_trigger: ".o_form_view",
                },

                // Flow 4 — Click OK on the confirmation dialog.
                {
                    content: "Confirm the dialog",
                    trigger: ".modal-footer button.btn-primary",
                    in_modal: true,
                },

                // ── Post-Condition — Status changes directly to Done
                // (no separate manual Done step), and approving
                // posted the accounting entry.
                {
                    content: "Status is Done",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='done'].btn-primary",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
                {
                    // A *readonly* many2one in 14.0 (`move_id` is
                    // always `readonly=True`) renders as a bare
                    // `<a class="o_form_uri o_field_widget ...">`, not
                    // `.o_field_many2one` (odoo-development-ui-test
                    // references/selectors.md §8).
                    content: "The Move field is filled",
                    trigger: ".o_field_widget[name='move_id'].o_form_uri",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
            ])
        );
    }
);
