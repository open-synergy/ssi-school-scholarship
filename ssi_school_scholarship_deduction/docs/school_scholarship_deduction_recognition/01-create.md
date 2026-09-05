# Create Scholarship Deduction Recognition

> **Module:** ssi_school_scholarship_deduction\
> **Model:** `school_scholarship_deduction_recognition`\
> **Menu:** School > Scholarship > Scholarship Deduction Recognitions\
> **Actor:** user in group `Deduction User`\
> **State:** `—` → `draft`

## Pre-Condition

- **Record:** A `school_scholarship_deduction` exists with `recognition_method` set to
  **Deferred** and `amount_deferred` greater than zero.
- **Config:** An active `policy.template` for this model grants `confirm_ok` for state
  `draft` to the actor's group (needed later by the confirm step).
- **Access:** User is in group `Deduction User`.

## Flow

1. Open the **School > Scholarship > Scholarship Deduction Recognitions** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Deduction** _(required)_: Select the deferred deduction document this document
     releases. Selecting it fills **Journal** (on the **Accounting** tab) from the
     deduction's own Recognition Journal and **Amount** from the deduction's own Amount
     Deferred.
   - **Amount** _(required)_: Defaulted from the selected Deduction's own Amount
     Deferred; may be lowered for a partial (amortized) release. The sum of every Done
     Recognition's Amount on the same Deduction may not exceed that Deduction's own
     Amount Total.
   - **Date**: Defaults to today's date. May not be earlier than the Deduction's own
     Date.
   - On the **Accounting** tab:
     - **Journal** _(required)_: Defaulted from the selected Deduction; may be
       overridden.
4. Click **Save**.

## Post-Condition

- A new Scholarship Deduction Recognition record is created in **Draft** status.
- **Ratio** (this document's own Amount divided by the Deduction's own Amount Total) is
  computed automatically.
