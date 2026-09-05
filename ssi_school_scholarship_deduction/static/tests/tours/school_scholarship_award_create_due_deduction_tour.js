// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define(
    "ssi_school_scholarship_deduction.school_scholarship_award_create_due_deduction_tour",
    function (require) {
        "use strict";

        var tour = require("web_tour.tour");

        // Shared navigation block -- Flow step 1 of
        // docs/school_scholarship_award/07-create-due-deduction.md:
        // "Open the School > Scholarship > Scholarship Awards menu."
        function openScholarshipAwardsList() {
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
                    content: "Open the Scholarship Awards menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_school_scholarship.school_scholarship_award_menu"]',
                },
                {
                    // Gate: wait for the Scholarship Awards action to
                    // actually be mounted, not just any list view left
                    // over from the landing action (patterns.md §A).
                    content: "Scholarship Awards list is displayed",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Scholarship Awards)",
                    extra_trigger: ".o_list_view",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
            ];
        }

        // IK: docs/school_scholarship_award/07-create-due-deduction.md
        tour.register(
            "ssi_school_scholarship_deduction_school_scholarship_award_create_due_deduction",
            {
                test: true,
                url: "/web",
            },
            [].concat(openScholarshipAwardsList(), [
                // Flow 2 — Open the record whose due Schedule will be
                // realized.
                {
                    content: "Open the record",
                    trigger:
                        ".o_data_row:contains(TOUR-AWARD-CREATEDEDUCTION-001) .o_data_cell:first",
                },
                {
                    content: "Form is open",
                    trigger: ".o_form_view",
                    extra_trigger: ".o_form_view.o_form_readonly",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },

                // Flow 3 — Click the Create Due Deduction button.
                {
                    content: "Click the Create Due Deduction button",
                    trigger:
                        ".o_statusbar_buttons button[name='action_open_create_due_deduction_wizard']",
                    extra_trigger: ".o_form_view",
                },

                // ── Flow 4/5 — The wizard opens with the Award already
                // pre-filled (not shown on the form); fill in Date End.
                // 14.0 does not prefix in-modal triggers with `.modal`
                // (odoo-development-ui-test, patterns.md §H note).
                {
                    content: "Wizard is open",
                    trigger: ".o_field_widget[name='date_end']",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
                {
                    content: "Fill in Date End",
                    trigger: ".o_field_widget[name='date_end'] input",
                    run: "text 12/31/2026",
                },

                // Flow 6 — Click Create Due Deduction in the wizard
                // footer.
                {
                    content: "Click Create Due Deduction in the wizard",
                    trigger: ".modal-footer button[name='action_create_due_deduction']",
                },

                // ── Post-Condition — the newly created Deduction
                // document is listed in the Scholarship Deductions
                // list, still in Draft
                // (docs/school_scholarship_award/07-create-due-
                // deduction.md:41). award_id is optional="hide" on
                // this tree (odoo-development-backlog#86), so the
                // Award's own name is not in the DOM; partner_id
                // (always-visible) renders the Student Contact's name
                // instead -- school_scholarship_deduction.partner_id
                // is related="award_id.partner_id", i.e.
                // student_id.contact_id. The wizard's own action
                // domain (`[("id", "in", deductions.ids)]`) already
                // scopes this list to only the Deduction(s) just
                // created, so this token is unique in the resulting
                // list regardless of how many other Deductions exist
                // in the database. The Draft gate is guaranteed false
                // until the wizard's own RPC actually finishes
                // (patterns.md §P): no such row exists before this
                // wizard is run.
                {
                    content: "Scholarship Deductions list is displayed",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Scholarship Deductions)",
                    extra_trigger: ".o_list_view",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
                {
                    content: "A Deduction for the Award appears in Draft",
                    trigger:
                        ".o_data_row:contains(TOUR CDD Student Contact):contains(Draft)",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
            ])
        );
    }
);
