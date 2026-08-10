// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define(
    "ssi_school_scholarship_admission.school_scholarship_award_tour",
    function (require) {
        "use strict";

        var tour = require("web_tour.tour");

        // IK: docs/school_scholarship_award/01-create.md ("Additional Fields"
        // delta). Navigation (open menu -> New -> select Program/Student) is
        // taken from the base IK
        // ssi_school_scholarship/docs/school_scholarship_award/01-create.md
        // Flow steps 1-3 -- see skill odoo-development-ui-test,
        // scope-and-boundaries.md §1 ("Backing dua file: tour extension =
        // base IK ∪ delta IK"). The delta itself: switching Billing Source
        // to Admission reveals the Admission field (in place of Enrollment),
        // selecting an Admission fills Student automatically, and the
        // record is saved -- the tour verifies the field is present and
        // the document is saved, not the field's value (that is
        // odoo-development-unit-test's job).
        tour.register(
            "ssi_school_scholarship_admission_school_scholarship_award_create",
            {
                test: true,
                url: "/web",
            },
            [
                // ── Base Flow 1 — Open the School > Scholarship >
                // Scholarship Awards menu.
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
                    content: "Open the Scholarship Awards menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_school_scholarship.school_scholarship_award_menu"]',
                },
                {
                    // Gate: wait for the TARGET action to be mounted, not
                    // just any list view (patterns.md §A).
                    content: "Scholarship Awards list is displayed",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Scholarship Awards)",
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

                // ── Base Flow 3 (partial) — Select Program and Student.
                {
                    content: "Select the Program",
                    trigger: ".o_field_many2one[name='program_id'] input",
                    run: "text TOUR ADM Award Program",
                },
                {
                    content: "Pick the Program from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR ADM Award Program)",
                    in_modal: false,
                },
                {
                    content: "Select the Student",
                    trigger: ".o_field_many2one[name='student_id'] input",
                    run: "text TOUR ADM Award Student",
                },
                {
                    content: "Pick the Student from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR ADM Award Student)",
                    in_modal: false,
                },

                // ── Delta — switch Billing Source to Admission, which
                // hides Enrollment and reveals the Admission field.
                {
                    content: "Switch Billing Source to Admission",
                    trigger: "select.o_field_widget[name='source_type']",
                    run: "text Admission",
                },
                {
                    content: "Admission field is now displayed",
                    trigger: ".o_field_many2one[name='admission_id']",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
                {
                    content: "Select the Admission",
                    trigger: ".o_field_many2one[name='admission_id'] input",
                    run: "text TOUR-ADM-AWARD-ADM-001",
                },
                {
                    content: "Pick the Admission from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR-ADM-AWARD-ADM-001)",
                    in_modal: false,
                },

                // ── Base Flow 3 (partial) — fill the remaining required
                // fields so the record can be saved.
                {
                    content: "Fill in Start Date",
                    trigger: ".o_field_widget[name='date_start'] input",
                    run: "text 07/01/2026",
                },
                {
                    content: "Fill in End Date",
                    trigger: ".o_field_widget[name='date_end'] input",
                    run: "text 12/31/2026",
                },

                // ── Base Flow 8 — Click Save.
                {
                    content: "Save the record",
                    trigger: ".o_form_button_save",
                },
                {
                    content: "Record is saved",
                    trigger: ".o_form_view.o_form_readonly",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
            ]
        );
    }
);
