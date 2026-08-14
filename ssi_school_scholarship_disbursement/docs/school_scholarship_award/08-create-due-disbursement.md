# Create Due Disbursement — Scholarship Award

> **Module:** ssi_school_scholarship_disbursement\
> **Extends:** ssi_school_scholarship — model `school_scholarship_award`\
> **Model:** `school_scholarship_award`\
> **Menu:** School > Scholarship > Scholarship Awards\
> **Actor:** user in group `Award User`\
> **State:** `open` (no state change)\
> **Requires:** ssi_school_scholarship/school_scholarship_award/05-approve

## Pre-Condition

- **Record:** Status is **On Progress**.
- **Record:** At least one Cash Schedule line whose own Benefit is a Cash benefit and
  whose state is still **Scheduled** (not yet realized into a Disbursement). An Award
  whose Schedule lines belong to a Fee Reduction benefit, or that are already realized,
  is left untouched.
- **Access:** User is in group `Award User`.

## Flow

1. Open the **School > Scholarship > Scholarship Awards** menu.
2. Either open a single Award's record, or select one or more Award rows directly in the
   list view.
3. Click the **Create Due Disbursement** button
   (`action_open_create_due_disbursement_wizard`).
4. In the **Create Due Scholarship Disbursement** wizard, the selected Award(s) are
   pre-filled (not shown on the form).
5. Fill in the fields:
   - **Date Start**: Optional. Lower bound (inclusive) on the Schedule line's Date.
     Leave empty for no lower bound.
   - **Date End**: Required. Upper bound (inclusive) on the Schedule line's Date.
6. Click **Create Due Disbursement** (`action_create_due_disbursement`) in the wizard
   footer.

## Post-Condition

- One draft `school_scholarship_disbursement` document is created for each selected
  Award that has at least one due Cash Schedule line, covering every such due line --
  across every Funding line -- as the document's own Lines; an Award with no due Cash
  Schedule line is skipped without error.
- Each created document is opened in the Scholarship Disbursements list, still in
  **Draft** status -- it is not confirmed automatically.
- Every realized Schedule line's own state is left as **Scheduled**; it only becomes
  **Realized** once its own Disbursement document is later opened.
- If none of the selected Award(s) had a due Cash Schedule line, the wizard raises an
  error instead of opening an empty list.
