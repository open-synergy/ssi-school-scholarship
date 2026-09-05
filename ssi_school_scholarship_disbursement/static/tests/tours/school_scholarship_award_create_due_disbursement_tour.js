// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define(
    "ssi_school_scholarship_disbursement.school_scholarship_award_create_due_disbursement_tour",
    function (require) {
        "use strict";

        var tour = require("web_tour.tour");

        // Shared navigation block -- Flow step 1 of
        // docs/school_scholarship_award/08-create-due-disbursement.md:
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

        // IK: docs/school_scholarship_award/08-create-due-disbursement.md
        tour.register(
            "ssi_school_scholarship_disbursement_school_scholarship_award_create_due_disbursement",
            {
                test: true,
                url: "/web",
            },
            [].concat(openScholarshipAwardsList(), [
                // Flow 2 — Open the record whose due Cash Schedule will
                // be realized.
                {
                    content: "Open the record",
                    trigger:
                        ".o_data_row:contains(TOUR-AWARD-CREATEDISBURSEMENT-001) .o_data_cell:first",
                },
                {
                    content: "Form is open",
                    trigger: ".o_form_view",
                    extra_trigger: ".o_form_view.o_form_readonly",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },

                // Flow 3 — Click the Create Due Disbursement button.
                {
                    content: "Click the Create Due Disbursement button",
                    trigger:
                        ".o_statusbar_buttons button[name='action_open_create_due_disbursement_wizard']",
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

                // Flow 6 — Click Create Due Disbursement in the wizard
                // footer.
                {
                    content: "Click Create Due Disbursement in the wizard",
                    trigger:
                        ".modal-footer button[name='action_create_due_disbursement']",
                },

                // ── Post-Condition — the newly created Disbursement
                // document is listed in the Scholarship Disbursements
                // list. The wizard's own action opens that list scoped
                // to `domain=[("id", "in", disbursements.ids)]`
                // (wizards/create_due_scholarship_disbursement.py,
                // `_open_disbursements`), so every row shown there was
                // just created by this run -- no row can pre-exist to
                // collide with the gate below.
                //
                // `award_id` is `optional="hide"` in this tree (issue
                // #87), so the Award's own name -- used by the previous
                // version of this gate -- is no longer in the DOM at
                // all. The default-visible columns are `date`,
                // `partner_id`, `amount_total`; `partner_id` here is
                // the Award's `student_id.contact_id` ("TOUR CDDB
                // Student Contact", set up in this file's own
                // setUpClass), paired with the Draft state badge so the
                // gate cannot also match a later state of the same row.
                {
                    content: "Scholarship Disbursements list is displayed",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Scholarship Disbursements)",
                    extra_trigger: ".o_list_view",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
                {
                    content: "A Disbursement for the Award appears in Draft",
                    trigger:
                        ".o_data_row:contains(TOUR CDDB Student Contact):contains(Draft)",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
            ])
        );
    }
);
