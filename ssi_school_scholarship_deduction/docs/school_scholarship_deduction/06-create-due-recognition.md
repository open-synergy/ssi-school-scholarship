# Create Due Recognition — Scholarship Deduction

> **Module:** ssi_school_scholarship_deduction\
> **Model:** `school_scholarship_deduction`\
> **Menu:** School > Scholarship > Scholarship Deductions\
> **Actor:** user in group `Deduction User`\
> **State:** `open` (no state change)

## Pre-Condition

- **Record:** At least one Deduction record exists in **On Progress** status with
  `recognition_method` **Deferred** and `recognition_state` **Pending** -- its own
  `amount_deferred` is greater than zero and not yet fully recognized.
- **Access:** User is in group `Deduction User`.

## Flow

1. Open the **School > Scholarship > Scholarship Deductions** menu.
2. Select at least one Deduction row in the list -- the **Create Due Recognition**
   button only appears in the list header once at least one row is selected.
3. Click the **Create Due Recognition** button in the list header.
4. In the **Create Due Scholarship Recognition** wizard:
   - **Date** _(required)_: Defaults to today. **Deductions** is filled with every
     Deduction whose own Recognition Status is Pending and whose own Recognition Date
     falls on or before this Date -- independently of which row(s) were selected in step
     2; changing Date refreshes the list.
   - **Deductions**: Read-only, widget many2many tags. Not editable by hand -- always
     mirrors the rule above.
5. Click **Create Due Recognition** (`action_create_due_recognition`) in the wizard
   footer.

## Post-Condition

- One draft `school_scholarship_deduction_recognition` document is created per Deduction
  listed in the wizard's Deductions field, each carrying that Deduction's own full
  Amount Deferred as its Amount, the selected Date, and the Deduction's own Recognition
  Journal.
- The newly created documents are opened in the Scholarship Deduction Recognitions list,
  still in **Draft** status.
- Every source Deduction's own status is left unchanged -- this action creates new
  documents, it does not move the Deduction itself.
- If the Deductions field is empty when the footer button is clicked (no Deduction is
  due for recognition as of the selected Date), the wizard raises an error instead of
  opening an empty list.
