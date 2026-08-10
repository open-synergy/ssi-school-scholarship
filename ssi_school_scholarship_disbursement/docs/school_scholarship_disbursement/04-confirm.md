# Confirm Scholarship Disbursement

> **Module:** ssi_school_scholarship_disbursement\
> **Model:** `school_scholarship_disbursement`\
> **Menu:** School > Scholarship > Scholarship Disbursements\
> **Actor:** user in group `Disbursement User`\
> **State:** `draft` → `confirm`

## Pre-Condition

- **Record:** A Scholarship Disbursement record exists in **Draft** status, created per
  `01-create.md`.
- **Config:** An active `policy.template` grants `confirm_ok` for state `draft` to the
  actor's group.
- **Config:** An active `approval.template` for this model names an approver group
  (needed later by `05-approve`).
- **Access:** User is in group `Disbursement User`.

## Flow

1. Open the **School > Scholarship > Scholarship Disbursements** menu.
2. Open the Draft record to confirm.
3. Click the **Confirm** button in the statusbar.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- The document's status changes to **Waiting for Approval**.
