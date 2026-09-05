# Approve Scholarship Deduction Recognition

> **Module:** ssi_school_scholarship_deduction\
> **Model:** `school_scholarship_deduction_recognition`\
> **Menu:** School > Scholarship > Scholarship Deduction Recognitions\
> **Actor:** user in group `Deduction Validator` named as approver on the `approval.template`\
> **State:** `confirm` → `done`

## Pre-Condition

- **Record:** A Scholarship Deduction Recognition record exists in **Waiting for
  Approval** status, reached by clicking its own **Confirm** button from **Draft**.
- **Config:** An active `policy.template` grants `approve_ok` for state `confirm` to the
  active approver.
- **Access:** User is the active approver named on the document's own
  `approval.template`.

## Flow

1. Open the **School > Scholarship > Scholarship Deduction Recognitions** menu.
2. Open the record to approve.
3. Click the **Approve** button in the statusbar.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- The document's status changes directly to **Done** -- this model has no separate
  manual Done step; approval both approves and finalizes the document.
- An `account.move` is created and posted, shown as this document's own Move on the
  **Accounting** tab: for every Line of the linked deduction, it debits that Line's own
  Final Account and credits its own Deferred Account, each pair for that Line's own
  Price Subtotal multiplied by Ratio (rounded to the currency's own precision, with the
  rounding remainder charged to the last pair), carrying that Line's own Analytic
  Account on both sides.
- The linked deduction's own **Amount Recognized** increases by this document's own
  Amount, **Amount Deferred** drops by the same, and **Recognition Status** becomes
  **Partially Recognized** or **Recognized** depending on whether any deferred amount
  remains.
