// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define("ssi_school_scholarship.school_scholarship_award_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    // Shared navigation block, reused verbatim by every tour below --
    // Flow step 1 of every IK in docs/school_scholarship_award/: "Open
    // the School > Scholarship > Scholarship Awards menu." Scholarship
    // Awards sits directly under the "Scholarship" section (unlike
    // Programs/Types/Funding Sources, which sit one level deeper under
    // "Configuration"), but 14.0 still lists it via a single click on
    // the "Scholarship" section header (odoo-development-ui-test,
    // patterns.md §A).
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

    // IK: docs/school_scholarship_award/01-create.md
    tour.register(
        "ssi_school_scholarship_school_scholarship_award_create",
        {
            test: true,
            url: "/web",
        },
        [].concat(openScholarshipAwardsList(), [
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

            // ── Flow 3 — Fill in Program, Student, Enrollment, Start
            // Date, End Date. Selecting Program triggers the onchange
            // that fills the nine accounting fields and Is Employee
            // Benefit in the background -- reviewed later in Flow 7,
            // once the Deduction tab is actually open.
            {
                content: "Select the Program",
                trigger: ".o_field_many2one[name='program_id'] input",
                run: "text TOUR Award Program",
            },
            {
                content: "Pick the Program from the dropdown",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR Award Program)",
                in_modal: false,
            },
            {
                content: "Select the Student",
                trigger: ".o_field_many2one[name='student_id'] input",
                run: "text TOUR Award Student",
            },
            {
                content: "Pick the Student from the dropdown",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR Award Student)",
                in_modal: false,
            },
            {
                content: "Select the Enrollment",
                trigger: ".o_field_many2one[name='enrollment_id'] input",
                run: "text TOUR-AWARD-ENR-001",
            },
            {
                content: "Pick the Enrollment from the dropdown",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR-AWARD-ENR-001)",
                in_modal: false,
            },
            {
                content: "Fill in the Start Date",
                trigger: ".o_field_widget[name='date_start'] input",
                run: "text 07/01/2026",
            },
            {
                content: "Fill in the End Date",
                trigger: ".o_field_widget[name='date_end'] input",
                run: "text 12/31/2026",
            },

            // ── Flow 4 — On the Benefit tab, add one line: Product and
            // Price Unit. Benefit Type, Computation, Periodicity keep
            // their defaults (Fee Reduction / Percentage / Per Payment
            // Term); Scope is left empty for this ad hoc line.
            {
                content: "Open the Benefit tab",
                trigger: ".o_notebook .nav-link:contains(Benefit)",
            },
            {
                content: "Add a Benefit line",
                trigger:
                    ".o_field_widget[name='benefit_ids'] .o_field_x2many_list_row_add a",
            },
            {
                content: "Select the Product",
                trigger: ".o_selected_row .o_field_widget[name='product_id'] input",
                run: "text TOUR Award Product",
            },
            {
                content: "Pick the Product from the dropdown",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR Award Product)",
                in_modal: false,
            },
            {
                // Monetary fields in a 14.0 editable list render inside
                // a wrapping `.o_field_widget[name=...]`, unlike plain
                // Float -- the input is a descendant, not the anchor
                // itself.
                content: "Fill in the Price Unit",
                trigger: ".o_selected_row .o_field_widget[name='price_unit'] input",
                run: "text 1000000",
            },
            {
                // Commit the last edited cell -- never `press Tab`
                // (odoo-development-ui-test references/patterns.md §C).
                content: "Commit the Benefit line",
                trigger: ".o_selected_row .o_field_widget[name='product_id']",
                run: "click",
            },

            // ── Flow 5 — On the Funding tab, add one line: Funding
            // Source and Percentage 100.
            {
                content: "Open the Funding tab",
                trigger: ".o_notebook .nav-link:contains(Funding)",
            },
            {
                content: "Add a Funding line",
                trigger:
                    ".o_field_widget[name='funding_ids'] .o_field_x2many_list_row_add a",
            },
            {
                content: "Select the Funding Source",
                trigger:
                    ".o_selected_row .o_field_widget[name='funding_source_id'] input",
                run: "text TOUR Award Funding Source",
            },
            {
                content: "Pick the Funding Source from the dropdown",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR Award Funding Source)",
                in_modal: false,
            },
            {
                // Plain Float fields in a 14.0 editable list render as a
                // bare `<input>` -- the selector must target the input
                // directly, not an `.o_field_widget[name=...]`
                // descendant (odoo-development-ui-test
                // references/patterns.md, and the lesson from
                // ssi-school-scholarship PR #19/#20).
                content: "Fill in the Percentage",
                trigger: ".o_selected_row input[name='percentage']",
                run: "text 100",
            },
            {
                content: "Commit the Funding line",
                trigger: ".o_selected_row .o_field_widget[name='funding_source_id']",
                run: "click",
            },

            // ── Flow 7 — Review the accounting fields defaulted from
            // the Program on the Deduction tab. Opening the tab is
            // required before its fields can be asserted: they render
            // inside a Bootstrap `.tab-pane` kept `display:none` while
            // a different tab is active, so `.o_external_button` never
            // becomes `:visible` until this tab is opened.
            {
                content: "Open the Deduction tab",
                trigger: ".o_notebook .nav-link:contains(Deduction)",
            },
            {
                content: "Deduction Journal is filled by the onchange",
                trigger:
                    ".o_field_many2one[name='deduction_journal_id'] .o_external_button",
                run: function () {
                    // Assertion only; do not trigger the default click.
                },
            },

            // ── Flow 8 — Click Save.
            {
                content: "Save the record",
                trigger: ".o_form_button_save",
            },

            // ── Post-Condition — a new Scholarship Award record is
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

    // IK: docs/school_scholarship_award/04-confirm.md
    tour.register(
        "ssi_school_scholarship_school_scholarship_award_confirm",
        {
            test: true,
            url: "/web",
        },
        [].concat(openScholarshipAwardsList(), [
            // Flow 2 — Open the record to confirm.
            {
                content: "Open the record",
                trigger:
                    ".o_data_row:contains(TOUR-AWARD-CONFIRM-001) .o_data_cell:first",
            },
            {
                content: "Form is open",
                trigger: ".o_form_view",
                extra_trigger: ".o_form_view.o_form_readonly",
                run: function () {
                    // Assertion only; do not trigger the default click.
                },
            },

            // Flow 3 — Click the Confirm button.
            {
                content: "Click the Confirm button",
                trigger: ".o_statusbar_buttons button[name='action_confirm']",
                extra_trigger: ".o_form_view",
            },

            // Flow 4 — Click OK on the confirmation dialog.
            {
                content: "Confirm the dialog",
                trigger: ".modal-footer button.btn-primary",
                in_modal: true,
            },

            // Post-Condition — Status changes to Waiting for Approval.
            {
                content: "Status is Waiting for Approval",
                trigger:
                    ".o_statusbar_status .o_arrow_button[data-value='confirm'].btn-primary",
                run: function () {
                    // Assertion only; do not trigger the default click.
                },
            },
        ])
    );

    // IK: docs/school_scholarship_award/05-approve.md
    tour.register(
        "ssi_school_scholarship_school_scholarship_award_approve",
        {
            test: true,
            url: "/web",
        },
        [].concat(openScholarshipAwardsList(), [
            // Flow 2 — Open the record to approve.
            {
                content: "Open the record",
                trigger:
                    ".o_data_row:contains(TOUR-AWARD-APPROVE-001) .o_data_cell:first",
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
                trigger: ".o_statusbar_buttons button[name='action_approve_approval']",
                extra_trigger: ".o_form_view",
            },

            // Flow 4 — Click OK on the confirmation dialog.
            {
                content: "Confirm the dialog",
                trigger: ".modal-footer button.btn-primary",
                in_modal: true,
            },

            // Post-Condition — Status changes to On Progress (the
            // fixture's single validator level is fulfilled by admin,
            // the tour user, on the first Approve click).
            {
                content: "Status is On Progress",
                trigger:
                    ".o_statusbar_status .o_arrow_button[data-value='open'].btn-primary",
                run: function () {
                    // Assertion only; do not trigger the default click.
                },
            },
        ])
    );

    // IK: docs/school_scholarship_award/10-cancel.md
    tour.register(
        "ssi_school_scholarship_school_scholarship_award_cancel",
        {
            test: true,
            url: "/web",
        },
        [].concat(openScholarshipAwardsList(), [
            // Flow 2 — Open the record to cancel.
            {
                content: "Open the record",
                trigger:
                    ".o_data_row:contains(TOUR-AWARD-CANCEL-001) .o_data_cell:first",
            },
            {
                content: "Form is open",
                trigger: ".o_form_view",
                extra_trigger: ".o_form_view.o_form_readonly",
                run: function () {
                    // Assertion only; do not trigger the default click.
                },
            },

            // Flow 3 — Click the Cancel button. It is a `type="action"`
            // button, so its `name` attribute is a numeric action id
            // in the DOM; target it by label instead
            // (odoo-development-ui-test, selectors.md §4).
            {
                content: "Click the Cancel button",
                trigger: ".o_statusbar_buttons button:enabled:contains('Cancel')",
                extra_trigger: ".o_form_view",
            },

            // Flow 4 — In the wizard that appears, select the
            // Cancellation Reason.
            {
                // The wizard renders `cancel_reason_id` with
                // `widget="radio"`, not the default many2one
                // autocomplete -- select the matching radio item by
                // its label text.
                content: "Select the Cancellation Reason",
                trigger:
                    ".o_field_widget[name='cancel_reason_id'] .o_radio_item:contains(TOUR Award Cancel Reason) input",
                in_modal: true,
            },

            // Flow 5 — Click Confirm.
            {
                content: "Confirm the wizard",
                trigger: ".modal-footer button[name='action_confirm']",
            },

            // Flow 6 — Click OK on the confirmation dialog. The
            // wizard's Confirm button carries `confirm="Are you
            // sure?"` (mixin ssi_transaction_cancel_mixin), stacking a
            // second modal on top of the wizard; 14.0 scopes the
            // trigger search to the topmost visible modal.
            {
                content: "Confirm the dialog",
                trigger: ".modal-footer button.btn-primary",
                in_modal: true,
            },

            // Post-Condition — Status changes to Cancelled.
            {
                content: "Status is Cancelled",
                trigger:
                    ".o_statusbar_status .o_arrow_button[data-value='cancel'].btn-primary",
                run: function () {
                    // Assertion only; do not trigger the default click.
                },
            },
        ])
    );
});
