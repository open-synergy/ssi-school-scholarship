// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define(
    "ssi_school_scholarship_disbursement.school_scholarship_disbursement_tour",
    function (require) {
        "use strict";

        var tour = require("web_tour.tour");

        // Shared navigation block, reused verbatim by every tour below --
        // Flow step 1 of every IK in
        // docs/school_scholarship_disbursement/: "Open the School >
        // Scholarship > Scholarship Disbursements menu."
        function openScholarshipDisbursementsList() {
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
                    content: "Open the Scholarship Disbursements menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_school_scholarship_disbursement.school_scholarship_disbursement_menu"]',
                },
                {
                    // Gate: wait for the Scholarship Disbursements action
                    // to actually be mounted, not just any list view
                    // left over from the landing action (patterns.md
                    // §A).
                    content: "Scholarship Disbursements list is displayed",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Scholarship Disbursements)",
                    extra_trigger: ".o_list_view",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
            ];
        }

        // IK: docs/school_scholarship_disbursement/01-create.md
        tour.register(
            "ssi_school_scholarship_disbursement_school_scholarship_disbursement_create",
            {
                test: true,
                url: "/web",
            },
            [].concat(openScholarshipDisbursementsList(), [
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

                // ── Flow 3 — Fill in Award, Payment Method, Date, Date
                // Due, all still in the header.
                {
                    content: "Select the Award",
                    trigger: ".o_field_many2one[name='award_id'] input",
                    run: "text TOUR-DISBURSEMENT-AWARD-CREATE-001",
                },
                {
                    content: "Pick the Award from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR-DISBURSEMENT-AWARD-CREATE-001)",
                    in_modal: false,
                },
                {
                    // Payment Method defaults to Bank Transfer, which
                    // makes Bank Account required (see the view's own
                    // attrs). Switching to Cash here avoids adding a
                    // Bank Account fixture just for this tour --
                    // matching the "cash" fixtures already used by the
                    // confirm/approve/cancel tours' own setUpClass.
                    // 14.0's <select> carries the o_field_widget class
                    // itself (not wrapped in a div), so the selector is
                    // a tag+class combination, not a descendant one
                    // (odoo-development-ui-test references/patterns.md
                    // §Field selection).
                    content: "Select Cash as the Payment Method",
                    trigger: "select.o_field_widget[name='payment_method']",
                    run: "text Cash",
                },
                {
                    // Date defaults to today() (see the model's own
                    // ``default=``), which drifts forward every day
                    // this tour runs. Filling it in explicitly here,
                    // no later than Date Due below, makes
                    // ``_check_date_due`` compare two fixed literals
                    // against each other instead of against
                    // ``fields.Date.today()`` -- the same pattern
                    // already used and green for
                    // ``date_start``/``date_end`` in
                    // ``school_scholarship_award_tour.js``.
                    content: "Fill in Date",
                    trigger: ".o_field_widget[name='date'] input",
                    run: "text 08/01/2026",
                },
                {
                    content: "Fill in Date Due",
                    trigger: ".o_field_widget[name='date_due'] input",
                    run: "text 08/15/2026",
                },

                // ── Flow 4 — On the Accounting tab, fill in Journal and
                // Payable Account -- both now live on the "Accounting"
                // page rather than the header (issue #87).
                {
                    content: "Open the Accounting tab",
                    trigger: ".o_notebook .nav-link:contains(Accounting)",
                },
                {
                    content: "Select the Journal",
                    trigger:
                        ".tab-pane.active .o_field_many2one[name='journal_id'] input",
                    run: "text TOUR Disbursement Cash Journal",
                },
                {
                    content: "Pick the Journal from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR Disbursement Cash Journal)",
                    in_modal: false,
                },
                {
                    content: "Select the Payable Account",
                    trigger:
                        ".tab-pane.active .o_field_many2one[name='payable_account_id'] input",
                    run: "text TOUR Disbursement Payable Account",
                },
                {
                    content: "Pick the Payable Account from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR Disbursement Payable Account)",
                    in_modal: false,
                },

                // ── Flow 5 — On the Lines tab, add one line: Schedule
                // and Funding. Selecting Schedule fills Description,
                // Product, and Final Account; selecting Funding,
                // together with Schedule, fills Price Unit.
                {
                    content: "Open the Lines tab",
                    trigger: ".o_notebook .nav-link:contains(Lines)",
                },
                {
                    content: "Add a Line",
                    trigger:
                        ".o_field_widget[name='line_ids'] .o_field_x2many_list_row_add a",
                },
                {
                    content: "Select the Schedule",
                    trigger:
                        ".o_selected_row .o_field_widget[name='schedule_id'] input",
                    run: "text 2026-08-01",
                },
                {
                    content: "Pick the Schedule from the dropdown",
                    trigger: ".ui-autocomplete .ui-menu-item a:contains(2026-08-01)",
                    in_modal: false,
                },
                {
                    content: "Select the Funding",
                    trigger: ".o_selected_row .o_field_widget[name='funding_id'] input",
                    run: "text TOUR Disbursement Funding Source",
                },
                {
                    content: "Pick the Funding from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR Disbursement Funding Source)",
                    in_modal: false,
                },
                {
                    // Gate (odoo-development-ui-test
                    // references/patterns.md §P): wait for the Funding
                    // onchange's RPC to land before touching the row
                    // again. Price Subtotal is a plain compute (no
                    // explicit `readonly`, so no inverse) and always
                    // renders as a static text node even mid-row-edit,
                    // unlike Price Unit's own `<input>` -- see the "m2o
                    // tak terbaca di mode edit" trap in patterns.md §L
                    // for why an editable widget's live value can never
                    // be the gate itself.
                    content:
                        "Price Subtotal reflects the Funding onchange before continuing",
                    trigger:
                        ".o_selected_row .o_field_widget[name='price_subtotal']:contains(500,000.00)",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
                {
                    // Commit the last edited cell -- never `press Tab`
                    // (odoo-development-ui-test references/patterns.md
                    // §C).
                    content: "Commit the Line",
                    trigger: ".o_selected_row .o_field_widget[name='uom_quantity']",
                    run: "click",
                },

                // ── Flow 6 — Click Save.
                {
                    content: "Save the record",
                    trigger: ".o_form_button_save",
                },

                // ── Post-Condition — a new Scholarship Disbursement
                // record is created in Draft status.
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

        // IK: docs/school_scholarship_disbursement/04-confirm.md
        tour.register(
            "ssi_school_scholarship_disbursement_school_scholarship_disbursement_confirm",
            {
                test: true,
                url: "/web",
            },
            [].concat(openScholarshipDisbursementsList(), [
                // Flow 2 — Open the record to confirm.
                {
                    content: "Open the record",
                    trigger:
                        ".o_data_row:contains(TOUR-DISBURSEMENT-CONFIRM-001) .o_data_cell:first",
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

        // IK: docs/school_scholarship_disbursement/05-approve.md
        tour.register(
            "ssi_school_scholarship_disbursement_school_scholarship_disbursement_approve",
            {
                test: true,
                url: "/web",
            },
            [].concat(openScholarshipDisbursementsList(), [
                // Flow 2 — Open the record to approve.
                {
                    content: "Open the record",
                    trigger:
                        ".o_data_row:contains(TOUR-DISBURSEMENT-APPROVE-001) .o_data_cell:first",
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

                // ── Post-Condition — Status changes to On Progress, and
                // opening posted the accounting entry. Waiting directly
                // for the Payable Move Line to appear is the only gate
                // here that is guaranteed false until the button's RPC
                // actually finishes (patterns.md §P): the field is
                // empty before this button is clicked.
                {
                    content: "Status is On Progress",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='open'].btn-primary",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },

                // Flow 5 — Open the Accounting tab to see the posting.
                {
                    content: "Open the Accounting tab",
                    trigger: ".o_notebook .nav-link:contains(Accounting)",
                },
                {
                    // A *readonly* many2one in 14.0 (`payable_move_line_id`
                    // is always `readonly=True`) renders as a bare
                    // `<a class="o_form_uri o_field_widget ...">` -- it
                    // never gets the `.o_field_many2one` wrapper class,
                    // which only applies in edit mode. Confirmed via the
                    // CI job's own DOM dump: the element exists and is
                    // filled, but `.o_field_many2one[name='...'] a`
                    // matches nothing (odoo-development-ui-test
                    // references/selectors.md §8, "Field readonly").
                    content: "The Payable Move Line field is filled",
                    trigger:
                        ".tab-pane.active .o_field_widget[name='payable_move_line_id'].o_form_uri",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
            ])
        );

        // IK: docs/school_scholarship_disbursement/10-cancel.md
        tour.register(
            "ssi_school_scholarship_disbursement_school_scholarship_disbursement_cancel",
            {
                test: true,
                url: "/web",
            },
            [].concat(openScholarshipDisbursementsList(), [
                // Flow 2 — Open the record to cancel.
                {
                    content: "Open the record",
                    trigger:
                        ".o_data_row:contains(TOUR-DISBURSEMENT-CANCEL-001) .o_data_cell:first",
                },
                {
                    content: "Form is open",
                    trigger: ".o_form_view",
                    extra_trigger: ".o_form_view.o_form_readonly",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },

                // Flow 3 — Click the Cancel button. It is a
                // `type="action"` button, so its `name` attribute is a
                // numeric action id in the DOM; target it by label
                // instead (odoo-development-ui-test, selectors.md §4).
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
                        ".o_field_widget[name='cancel_reason_id'] .o_radio_item:contains(TOUR Disbursement Cancel Reason) input",
                    in_modal: true,
                },

                // Flow 5 — Click Confirm.
                {
                    content: "Confirm the wizard",
                    trigger: ".modal-footer button[name='action_confirm']",
                },

                // Flow 6 — Click OK on the confirmation dialog. The
                // wizard's Confirm button carries `confirm="Are you
                // sure?"` (mixin ssi_transaction_cancel_mixin), stacking
                // a second modal on top of the wizard; 14.0 scopes the
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
    }
);
