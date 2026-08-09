# Approve Scholarship Award

> **Module:** ssi_school_scholarship\
> **Model:** `school_scholarship_award`\
> **Menu:** School > Scholarship > Scholarship Awards\
> **Actor:** approver on the pending approval level\
> **State:** `confirm` → `open`\
> **Requires:** `04-confirm`

## Pre-Condition

- **Record:** Status is **Waiting for Approval**.
- **Config:** An active `policy.template` grants `approve_ok` to the actor's group.
- **Access:** User is registered as an approver on the approval level that is currently
  **pending**.

## Flow

1. Open the **School > Scholarship > Scholarship Awards** menu.
2. Open the record to approve.
3. Click the **Approve** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- If all approval levels are fulfilled, status changes automatically to **On Progress**,
  shown on the statusbar, and the record's **# Document** number is assigned from the
  `SCH/` sequence (no longer showing `/`).
- Once **On Progress**, the award's **Amount Committed** is added to the Funding
  Source(s)' own `amount_committed`, and the Program's **Quota Used** is increased by
  one.
- If there are still pending approval levels, status remains **Waiting for Approval**
  and the next level becomes pending.
