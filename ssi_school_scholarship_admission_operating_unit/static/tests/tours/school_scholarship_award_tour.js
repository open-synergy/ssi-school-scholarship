// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define(
    "ssi_school_scholarship_admission_operating_unit.school_scholarship_award_tour",
    function (require) {
        "use strict";

        var tour = require("web_tour.tour");

        // IK: docs/school_scholarship_award/01-create.md ("Additional
        // Post-Condition" delta -- Operating Unit is derived from the
        // Admission's School, mirroring
        // ssi_school_scholarship_operating_unit's Enrollment-sourced
        // delta). Navigation (open menu -> New -> select
        // Program/Student, switch Billing Source to Admission, select
        // Admission) is taken from the base IK
        // ssi_school_scholarship/docs/school_scholarship_award/
        // 01-create.md Flow steps 1-3, plus the Billing Source/Admission
        // delta from
        // ssi_school_scholarship_admission/docs/school_scholarship_award/
        // 01-create.md ("Additional Fields") -- see skill
        // odoo-development-ui-test, scope-and-boundaries.md §1 ("Backing
        // dua file: tour extension = base IK ∪ delta IK"). This module's
        // own delta assertion comes last: selecting the Admission (which
        // also fills the read-only school_id via
        // ssi_school_scholarship_admission's widened compute) auto-fills
        // the Operating Unit field, visible here as the m2o "open
        // record" external button appearing -- not the field's exact
        // value, which is odoo-development-unit-test's job. The tour
        // stops there; it does not fill Dates/Benefit/Funding or save.
        tour.register(
            "ssi_school_scholarship_admission_operating_unit_school_scholarship_award_create",
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
                    run: "text TOUR ADMOU Award Program",
                },
                {
                    content: "Pick the Program from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item:not(.o_m2o_dropdown_option) a:contains(TOUR ADMOU Award Program)",
                    in_modal: false,
                },
                {
                    content: "Select the Student",
                    trigger: ".o_field_many2one[name='student_id'] input",
                    run: "text TOUR ADMOU Award Student",
                },
                {
                    content: "Pick the Student from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item:not(.o_m2o_dropdown_option) a:contains(TOUR ADMOU Award Student)",
                    in_modal: false,
                },

                // ── Delta (ssi_school_scholarship_admission) — switch
                // Billing Source to Admission, which hides Enrollment
                // and reveals the Admission field.
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
                    run: "text TOUR-ADMOU-AWARD-ADM-001",
                },
                {
                    content: "Pick the Admission from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item:not(.o_m2o_dropdown_option) a:contains(TOUR-ADMOU-AWARD-ADM-001)",
                    in_modal: false,
                },

                // ── This module's own delta assertion — the Operating
                // Unit field is auto-filled by this module's create/
                // write derivation reflected onto the form via
                // ssi_school_scholarship_operating_unit's onchange on
                // school_id (itself following admission_id through
                // ssi_school_scholarship_admission's widened
                // _compute_school_id). The "open record" external
                // button on a many2one only renders once the field
                // carries a value, so its presence is proof of "filled"
                // without asserting which operating unit it holds
                // (odoo-development-ui-test, scope-and-boundaries.md §2
                // -- exact value belongs to odoo-development-unit-test).
                {
                    content: "Operating Unit is auto-filled from the Admission's School",
                    trigger:
                        ".o_field_many2one[name='operating_unit_id'] .o_external_button",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
            ]
        );
    }
);
