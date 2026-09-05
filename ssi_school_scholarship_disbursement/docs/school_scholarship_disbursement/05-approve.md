# Approve Scholarship Disbursement

> **Module:** ssi_school_scholarship_disbursement\
> **Model:** `school_scholarship_disbursement`\
> **Menu:** School > Scholarship > Scholarship Disbursements\
> **Actor:** user in group `Disbursement Validator` named as approver on the `approval.template`\
> **State:** `confirm` → `open`

## Pre-Condition

- **Record:** A Scholarship Disbursement record exists in **Waiting for Approval**
  status, produced by `04-confirm.md`.
- **Config:** An active `policy.template` grants `approve_ok` for state `confirm` to the
  active approver.
- **Access:** User is the active approver named on the document's `approval.template`.

## Flow

1. Open the **School > Scholarship > Scholarship Disbursements** menu.
2. Open the record to approve.
3. Click the **Approve** button in the statusbar.
4. Click **OK** on the confirmation dialog.
5. Open the **Accounting** tab to see the posting this created.

## Post-Condition

- The document's status changes to **On Progress**.
- An `account.move` is created and posted: it credits the document's Payable Account for
  Amount Total, and debits each Line's own account for its Price Subtotal, carrying that
  line's Analytic Account.
- On the **Accounting** tab, **Journal Entry** (`move_id`) now points to that posted
  `account.move`, and **Payable Move Line** (`payable_move_line_id`) points to its
  payable line — both are empty before this step.
- **Amount Residual** equals Amount Total and **Amount Paid** is zero — no
  `account.payment` has been linked yet.
- Every Cash Schedule line targeted by a Line on this document changes state to
  **Realized**.
