// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define(
    "ssi_school_scholarship_operating_unit.school_scholarship_award_tour",
    function (require) {
        "use strict";

        var tour = require("web_tour.tour");

        // IK: docs/school_scholarship_award/01-create.md ("Additional
        // Post-Condition" delta -- Operating Unit is derived, not
        // user-filled, mirroring ssi_school_operating_unit's
        // school_enrollment delta). Navigation (open menu -> New -> select
        // Program/Student/Enrollment) is taken from the base IK
        // ssi_school_scholarship/docs/school_scholarship_award/
        // 01-create.md Flow steps 1-3 -- see skill
        // odoo-development-ui-test, scope-and-boundaries.md §1 ("Backing
        // dua file: tour extension = base IK ∪ delta IK"). The delta
        // assertion comes from this module's own IK: selecting the
        // Enrollment (which also fills the related, read-only school_id)
        // auto-fills the Operating Unit field, visible here as the m2o
        // "open record" external button appearing -- not the field's
        // exact value, which is odoo-development-unit-test's job. The
        // tour stops there; it does not fill Dates/Benefit/Funding or
        // save.
        tour.register(
            "ssi_school_scholarship_operating_unit_school_scholarship_award_create",
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

                // ── Base Flow 3 (partial) — Select Program, Student, and
                // Enrollment. Selecting the Enrollment is what triggers
                // this module's derivation (its school_id ripples into
                // this record's related, read-only school_id, which this
                // module's onchange watches).
                {
                    content: "Select the Program",
                    trigger: ".o_field_many2one[name='program_id'] input",
                    run: "text TOUR OU Award Program",
                },
                {
                    content: "Pick the Program from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR OU Award Program)",
                    in_modal: false,
                },
                {
                    content: "Select the Student",
                    trigger: ".o_field_many2one[name='student_id'] input",
                    run: "text TOUR OU Award Student",
                },
                {
                    content: "Pick the Student from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR OU Award Student)",
                    in_modal: false,
                },
                {
                    content: "Select the Enrollment",
                    trigger: ".o_field_many2one[name='enrollment_id'] input",
                    run: "text TOUR-OU-AWARD-ENR-001",
                },
                {
                    content: "Pick the Enrollment from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR-OU-AWARD-ENR-001)",
                    in_modal: false,
                },

                // ── Delta assertion — the Operating Unit field is
                // auto-filled by the onchange this module registers on
                // school_id (which itself follows enrollment_id). The
                // "open record" external button on a many2one only
                // renders once the field carries a value, so its
                // presence is proof of "filled" without asserting which
                // operating unit it holds (odoo-development-ui-test,
                // scope-and-boundaries.md §2 -- exact value belongs to
                // odoo-development-unit-test).
                {
                    content: "Operating Unit is auto-filled by the onchange",
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
