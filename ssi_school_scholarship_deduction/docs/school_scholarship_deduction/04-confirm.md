# Confirm Scholarship Deduction

> **Module:** ssi_school_scholarship_deduction\
> **Model:** `school_scholarship_deduction`\
> **Menu:** School > Scholarship > Scholarship Deductions\
> **Actor:** user in group `Deduction User`\
> **State:** `draft` → `confirm`

## Pre-Condition

- **Record:** A Scholarship Deduction record exists in **Draft** status, created per
  `01-create.md`.
- **Config:** An active `policy.template` grants `confirm_ok` for state `draft` to the
  actor's group.
- **Config:** An active `approval.template` for this model names an approver group
  (needed later by `05-approve`).
- **Access:** User is in group `Deduction User`.

## Flow

1. Open the **School > Scholarship > Scholarship Deductions** menu.
2. Open the Draft record to confirm.
3. Click the **Confirm** button in the statusbar.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- The document's status changes to **Waiting for Approval**.
