// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define(
    "ssi_school_scholarship_deduction_operating_unit.school_scholarship_deduction_tour",
    function (require) {
        "use strict";

        var tour = require("web_tour.tour");

        // IK: docs/school_scholarship_deduction/01-create.md ("Additional
        // Post-Condition" delta -- Operating Unit is derived from the
        // selected Award, not user-filled). Navigation (open menu -> New
        // -> select Award) is taken from the base IK
        // ssi_school_scholarship_deduction/docs/school_scholarship_deduction/
        // 01-create.md Flow steps 1-3 -- see skill
        // odoo-development-ui-test, scope-and-boundaries.md §1 ("Backing
        // dua file: tour extension = base IK ∪ delta IK"). The delta
        // assertion comes from this module's own IK: selecting the Award
        // auto-fills the Operating Unit field, visible here as the m2o
        // "open record" external button appearing -- not the field's
        // exact value, which is odoo-development-unit-test's job. The
        // tour stops there; it does not fill Journal/Receivable
        // Account/Lines/Allocations or save.
        tour.register(
            "ssi_school_scholarship_deduction_operating_unit_school_scholarship_deduction_create",
            {
                test: true,
                url: "/web",
            },
            [
                // ── Base Flow 1 — Open the School > Scholarship >
                // Scholarship Deductions menu.
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
                    content: "Open the Scholarship Deductions menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_school_scholarship_deduction.school_scholarship_deduction_menu"]',
                },
                {
                    // Gate: wait for the TARGET action to be mounted, not
                    // just any list view (patterns.md §A).
                    content: "Scholarship Deductions list is displayed",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Scholarship Deductions)",
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

                // ── Base Flow 3 (partial) — Select the Award. Selecting
                // it is what triggers this module's own derivation.
                {
                    content: "Select the Award",
                    trigger: ".o_field_many2one[name='award_id'] input",
                    run: "text TOUR-DEDUCTION-OU-AWARD-001",
                },
                {
                    content: "Pick the Award from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR-DEDUCTION-OU-AWARD-001)",
                    in_modal: false,
                },

                // ── Delta assertion — the Operating Unit field is
                // auto-filled by the onchange this module registers on
                // award_id. The "open record" external button on a
                // many2one only renders once the field carries a value,
                // so its presence is proof of "filled" without asserting
                // which operating unit it holds
                // (odoo-development-ui-test, scope-and-boundaries.md §2
                // -- exact value belongs to odoo-development-unit-test).
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
