# Cancel Scholarship Award

> **Module:** ssi_school_scholarship\
> **Model:** `school_scholarship_award`\
> **Menu:** School > Scholarship > Scholarship Awards\
> **Actor:** user in group `Award Validator`\
> **State:** `draft` | `confirm` | `open` → `cancel`\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** Status is **Draft**, **Waiting for Approval**, or **On Progress**.
- **Config:** An active `policy.template` grants `cancel_ok` for that state to the
  actor's group.
- **Access:** User is in group `Award Validator`.

## Flow

1. Open the **School > Scholarship > Scholarship Awards** menu.
2. Open the record to cancel.
3. Click the **Cancel** button.
4. In the wizard that appears, select the **Cancellation Reason**.
5. Click **Confirm**.
6. Click **OK** on the confirmation dialog.

## Post-Condition

- Status changes to **Cancelled**, shown on the statusbar.
