# Restart Approval Process — Scholarship Award

> **Module:** ssi_school_scholarship\
> **Model:** `school_scholarship_award`\
> **Menu:** School > Scholarship > Scholarship Awards\
> **Actor:** user in group `Award Validator`\
> **Requires:** `05-approve`

## Pre-Condition

- **Record:** Status is **On Progress**, and the approval process is stalled (for
  example, the record currently has no approval template assigned).
- **Config:** An active `policy.template` for this model grants `restart_approval_ok`
  for state `open` to the actor's group.
- **Access:** User is in group `Award Validator`.

## Flow

1. Open the **School > Scholarship > Scholarship Awards** menu.
2. Open the record whose approval process is stalled.
3. Click the **Restart Approval Process** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- Status remains **On Progress**.
- The existing approval records are discarded and a new approval process is created from
  the approval template that now matches the record, if any.
