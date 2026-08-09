# Approve Scholarship Deduction

> **Module:** ssi_school_scholarship_deduction\
> **Model:** `school_scholarship_deduction`\
> **Menu:** School > Scholarship > Scholarship Deductions\
> **Actor:** user in group `Deduction Validator` named as approver on the `approval.template`\
> **State:** `confirm` → `open`

## Pre-Condition

- **Record:** A Scholarship Deduction record exists in **Waiting for Approval** status,
  produced by `04-confirm.md`.
- **Config:** An active `policy.template` grants `approve_ok` for state `confirm` to the
  active approver.
- **Access:** User is the active approver named on the document's `approval.template`.

## Flow

1. Open the **School > Scholarship > Scholarship Deductions** menu.
2. Open the record to approve.
3. Click the **Approve** button in the statusbar.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- The document's status changes to **On Progress**.
- An `account.move` is created and posted: it credits the document's Receivable Account
  for Amount Total, and debits each Line's own account for its Price Subtotal, carrying
  that line's Analytic Account.
- The document's Receivable journal item is reconciled against every allocated invoice's
  own receivable journal item — each invoice's Amount Residual drops by its Amount
  Allocated, and an invoice fully covered moves to **Paid**.
- Every Schedule line targeted by a Line on this document changes state to **Realized**.
