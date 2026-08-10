# Cancel Scholarship Disbursement

> **Module:** ssi_school_scholarship_disbursement\
> **Model:** `school_scholarship_disbursement`\
> **Menu:** School > Scholarship > Scholarship Disbursements\
> **Actor:** user in group `Disbursement Validator`\
> **State:** `draft` | `confirm` | `open` → `cancel`\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** Status is **Draft**, **Waiting for Approval**, or **On Progress**.
- **Config:** An active `policy.template` grants `cancel_ok` for that state to the
  actor's group.
- **Access:** User is in group `Disbursement Validator`.

## Flow

1. Open the **School > Scholarship > Scholarship Disbursements** menu.
2. Open the record to cancel.
3. Click the **Cancel** button.
4. In the wizard that appears, select the **Cancellation Reason**.
5. Click **Confirm**.
6. Click **OK** on the confirmation dialog.

## Post-Condition

- Status changes to **Cancelled**, shown on the statusbar.
- If the document was **On Progress**, its `account.move` is deleted and every Schedule
  line it had marked Realized returns to **Scheduled**.
