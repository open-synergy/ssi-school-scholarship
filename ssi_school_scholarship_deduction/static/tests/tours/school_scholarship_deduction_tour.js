// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define(
    "ssi_school_scholarship_deduction.school_scholarship_deduction_tour",
    function (require) {
        "use strict";

        var tour = require("web_tour.tour");

        // Shared navigation block, reused verbatim by every tour below --
        // Flow step 1 of every IK in docs/school_scholarship_deduction/:
        // "Open the School > Scholarship > Scholarship Deductions menu."
        function openScholarshipDeductionsList() {
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
                    content: "Open the Scholarship Deductions menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_school_scholarship_deduction.school_scholarship_deduction_menu"]',
                },
                {
                    // Gate: wait for the Scholarship Deductions action to
                    // actually be mounted, not just any list view left
                    // over from the landing action (patterns.md §A).
                    content: "Scholarship Deductions list is displayed",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Scholarship Deductions)",
                    extra_trigger: ".o_list_view",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
            ];
        }

        // IK: docs/school_scholarship_deduction/01-create.md
        tour.register(
            "ssi_school_scholarship_deduction_school_scholarship_deduction_create",
            {
                test: true,
                url: "/web",
            },
            [].concat(openScholarshipDeductionsList(), [
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

                // ── Flow 3 — Fill in Award, Journal, Receivable Account.
                {
                    content: "Select the Award",
                    trigger: ".o_field_many2one[name='award_id'] input",
                    run: "text TOUR-DEDUCTION-AWARD-CREATE-001",
                },
                {
                    content: "Pick the Award from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR-DEDUCTION-AWARD-CREATE-001)",
                    in_modal: false,
                },
                {
                    content: "Select the Journal",
                    trigger: ".o_field_many2one[name='journal_id'] input",
                    run: "text TOUR Deduction Sale Journal",
                },
                {
                    content: "Pick the Journal from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR Deduction Sale Journal)",
                    in_modal: false,
                },
                {
                    content: "Select the Receivable Account",
                    trigger: ".o_field_many2one[name='receivable_account_id'] input",
                    run: "text TOUR Deduction Receivable Account",
                },
                {
                    content: "Pick the Receivable Account from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR Deduction Receivable Account)",
                    in_modal: false,
                },

                // ── Flow 4 — On the Lines tab, add one line: Schedule
                // and Funding. Selecting Schedule fills Description,
                // Product, and Final Account; selecting Funding, together
                // with Schedule, fills Price Unit.
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
                    run: "text TOUR Deduction Funding Source",
                },
                {
                    content: "Pick the Funding from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR Deduction Funding Source)",
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
                        ".o_selected_row .o_field_widget[name='price_subtotal']:contains(400,000.00)",
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

                // ── Flow 5 — On the Allocations tab, add one line:
                // Customer Invoice and Amount Allocated.
                {
                    content: "Open the Allocations tab",
                    trigger: ".o_notebook .nav-link:contains(Allocations)",
                },
                {
                    content: "Add an Allocation",
                    trigger:
                        ".o_field_widget[name='allocation_ids'] .o_field_x2many_list_row_add a",
                },
                {
                    content: "Select the Customer Invoice",
                    trigger:
                        ".o_selected_row .o_field_widget[name='customer_invoice_id'] input",
                    run: "text TOUR-DEDUCTION-CREATE-001",
                },
                {
                    content: "Pick the Customer Invoice from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR-DEDUCTION-CREATE-001)",
                    in_modal: false,
                },
                {
                    // Monetary fields in a 14.0 editable list render
                    // inside a wrapping `.o_field_widget[name=...]`
                    // (odoo-development-ui-test references/patterns.md,
                    // ssi-school-scholarship PR #19/#20).
                    content: "Fill in the Amount Allocated",
                    trigger:
                        ".o_selected_row .o_field_widget[name='amount_allocated'] input",
                    run: "text 400000",
                },
                {
                    content: "Commit the Allocation",
                    trigger:
                        ".o_selected_row .o_field_widget[name='customer_invoice_id']",
                    run: "click",
                },

                // ── Flow 6 — Click Save.
                {
                    content: "Save the record",
                    trigger: ".o_form_button_save",
                },

                // ── Post-Condition — a new Scholarship Deduction record
                // is created in Draft status.
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

        // IK: docs/school_scholarship_deduction/04-confirm.md
        tour.register(
            "ssi_school_scholarship_deduction_school_scholarship_deduction_confirm",
            {
                test: true,
                url: "/web",
            },
            [].concat(openScholarshipDeductionsList(), [
                // Flow 2 — Open the record to confirm.
                {
                    content: "Open the record",
                    trigger:
                        ".o_data_row:contains(TOUR-DEDUCTION-CONFIRM-001) .o_data_cell:first",
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

        // IK: docs/school_scholarship_deduction/05-approve.md
        tour.register(
            "ssi_school_scholarship_deduction_school_scholarship_deduction_approve",
            {
                test: true,
                url: "/web",
            },
            [].concat(openScholarshipDeductionsList(), [
                // Flow 2 — Open the record to approve.
                {
                    content: "Open the record",
                    trigger:
                        ".o_data_row:contains(TOUR-DEDUCTION-APPROVE-001) .o_data_cell:first",
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
                // for the Receivable Move Line to appear is the only
                // gate here that is guaranteed false until the button's
                // RPC actually finishes (patterns.md §P): the field is
                // empty before this button is clicked.
                {
                    content: "Status is On Progress",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='open'].btn-primary",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
                {
                    // A *readonly* many2one in 14.0 (`receivable_move_line_id`
                    // is always `readonly=True`) renders as a bare
                    // `<a class="o_form_uri o_field_widget ...">` -- it
                    // never gets the `.o_field_many2one` wrapper class,
                    // which only applies in edit mode. Confirmed via the
                    // CI job's own DOM dump: the element exists and is
                    // filled, but `.o_field_many2one[name='...'] a`
                    // matches nothing (odoo-development-ui-test
                    // references/selectors.md §8, "Field readonly").
                    content: "The Receivable Move Line field is filled",
                    trigger:
                        ".o_field_widget[name='receivable_move_line_id'].o_form_uri",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
            ])
        );

        // IK: docs/school_scholarship_deduction/10-cancel.md
        tour.register(
            "ssi_school_scholarship_deduction_school_scholarship_deduction_cancel",
            {
                test: true,
                url: "/web",
            },
            [].concat(openScholarshipDeductionsList(), [
                // Flow 2 — Open the record to cancel.
                {
                    content: "Open the record",
                    trigger:
                        ".o_data_row:contains(TOUR-DEDUCTION-CANCEL-001) .o_data_cell:first",
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
                        ".o_field_widget[name='cancel_reason_id'] .o_radio_item:contains(TOUR Deduction Cancel Reason) input",
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

        // IK: docs/school_scholarship_deduction/06-create-due-recognition.md
        tour.register(
            "ssi_school_scholarship_deduction_school_scholarship_deduction_create_due_recognition",
            {
                test: true,
                url: "/web",
            },
            [].concat(openScholarshipDeductionsList(), [
                // Flow 2 — Select at least one Deduction row. The header
                // only renders the Create Due Recognition button once the
                // list has a non-empty selection (web/list_controller.js
                // ListController._renderHeaderButtons: "if
                // (!this.headerButtons.length || !this.selectedRecords
                // .length) { return; }").
                {
                    content: "Select the Deduction row",
                    trigger:
                        ".o_data_row:contains(TOUR-DEDUCTION-RECOGNITION-001) .o_list_record_selector input",
                    run: "click",
                },

                // Flow 3 — Click the Create Due Recognition button in the
                // list header. It is a `type="action"` button, so its
                // `name` attribute is a numeric action id in the DOM;
                // target it by label instead (odoo-development-ui-test,
                // selectors.md §4) -- the same reason 10-cancel.md's own
                // tour above targets its Cancel button this way.
                {
                    content: "Click the Create Due Recognition button",
                    trigger:
                        ".o_list_buttons button:contains('Create Due Recognition')",
                },

                // ── Flow 4 — The wizard opens with Date already defaulted
                // to today and Deductions already filled (both computed
                // server-side by default_get, independently of the row
                // selected in Flow 2). Nothing needs to be typed here.
                // 14.0 does not prefix in-modal triggers with `.modal`
                // (odoo-development-ui-test, patterns.md §H note).
                {
                    content: "Wizard is open",
                    trigger: ".o_field_widget[name='deduction_ids']",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },

                // Flow 5 — Click Create Due Recognition in the wizard
                // footer.
                {
                    content: "Click Create Due Recognition in the wizard",
                    trigger:
                        ".modal-footer button[name='action_create_due_recognition']",
                },

                // ── Post-Condition — the newly created Recognition
                // document is listed in the Scholarship Deduction
                // Recognitions list. Waiting for the source Deduction's
                // own name in the list is the only gate here that is
                // guaranteed false until the wizard's own RPC actually
                // finishes (patterns.md §P): no such row exists before
                // this wizard is run.
                {
                    content: "Scholarship Deduction Recognitions list is displayed",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Scholarship Deduction Recognitions)",
                    extra_trigger: ".o_list_view",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
                {
                    content: "A Recognition for the Deduction appears in Draft",
                    trigger: ".o_data_row:contains(TOUR-DEDUCTION-RECOGNITION-001)",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
            ])
        );
    }
);
