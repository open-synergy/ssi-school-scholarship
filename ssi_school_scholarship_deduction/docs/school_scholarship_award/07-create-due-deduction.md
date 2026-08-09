# Create Due Deduction — Scholarship Award

> **Module:** ssi_school_scholarship_deduction\
> **Extends:** ssi_school_scholarship — model `school_scholarship_award`\
> **Model:** `school_scholarship_award`\
> **Menu:** School > Scholarship > Scholarship Awards\
> **Actor:** user in group `Award User`\
> **State:** `open` (no state change)\
> **Requires:** ssi_school_scholarship/school_scholarship_award/05-approve

## Pre-Condition

- **Record:** Status is **On Progress**.
- **Record:** At least one Schedule line whose own Payment Term is **Invoiced** and
  whose invoice is **Open**. A line whose Payment Term is not yet invoiced, or already
  realized, is left untouched.
- **Config:** An active `policy.template` for this model grants `create_deduction_ok`
  for state `open` to the actor's group.
- **Access:** User is in group `Award User`.

## Flow

1. Open the **School > Scholarship > Scholarship Awards** menu.
2. Either open a single Award's record, or select one or more Award rows directly in the
   list view.
3. Click the **Create Due Deduction** button
   (`action_open_create_due_deduction_wizard`).
4. In the **Create Due Scholarship Deduction** wizard, the selected Award(s) are
   pre-filled (not shown on the form).
5. Fill in the fields:
   - **Date Start**: Optional. Lower bound (inclusive) on the Schedule line's Date.
     Leave empty for no lower bound.
   - **Date End**: Required. Upper bound (inclusive) on the Schedule line's Date.
6. Click **Create Due Deduction** (`action_create_due_deduction`) in the wizard footer.

## Post-Condition

- One draft `school_scholarship_deduction` document is created per distinct invoice
  among the due Schedule lines, grouped across every selected Award; an Award with no
  due Schedule line is skipped without error.
- Each created document is opened in the Scholarship Deductions list, still in **Draft**
  status -- it is not confirmed automatically.
- Every realized Schedule line's own state is left as **Scheduled**; it only becomes
  **Realized** once its own Deduction document is later opened.
- If none of the selected Award(s) had a due Schedule line, the wizard raises an error
  instead of opening an empty list.
