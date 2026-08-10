# Create Scholarship Disbursement

> **Module:** ssi_school_scholarship_disbursement\
> **Model:** `school_scholarship_disbursement`\
> **Menu:** School > Scholarship > Scholarship Disbursements\
> **Actor:** user in group `Disbursement User`\
> **State:** `—` → `draft`

## Pre-Condition

- **Data:** A `school_scholarship_award` exists, already `open`, with at least one Cash
  Schedule line (state `scheduled`, Benefit line `benefit_type` = `Cash`) and at least
  one Funding line.
- **Config:** An active `policy.template` for this model grants `confirm_ok` for state
  `draft` to the actor's group (needed later by `04-confirm`).
- **Access:** User is in group `Disbursement User`.

## Flow

1. Open the **School > Scholarship > Scholarship Disbursements** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Award** _(required)_: Select the scholarship award this disbursement realizes.
   - **Journal** _(required)_: Select the accounting journal this document posts to.
   - **Payable Account** _(required)_: Select the payable account this document credits.
     Must allow reconciliation, or opening this document is rejected (see `05-approve`).
   - **Payment Method** _(required)_: Select **Cash** or **Bank Transfer**. Defaults to
     Bank Transfer.
   - **Bank Account**: Required when Payment Method is Bank Transfer.
   - **Date**: Defaults to today's date.
   - **Date Due** _(required)_: Must not be earlier than Date.
4. On the **Lines** tab, add **at least one** line:
   - **Schedule** _(required)_: Select an Award Schedule line, restricted to the
     selected Award's own Schedule. Selecting it fills Description, Product, and Final
     Account from the Schedule line's Benefit.
   - **Funding** _(required)_: Select an Award Funding line, restricted to the selected
     Award's own Funding. Selecting it, together with Schedule, fills **Price Unit** as
     the Schedule line's Amount Planned multiplied by the Funding line's Percentage.
   - **UoM Quantity**: Left at its default of **1** — Price Unit is also this line's
     total.
5. Click **Save**.

## Post-Condition

- A new Scholarship Disbursement record is created in **Draft** status.
- **Amount Total** is recomputed from the Lines tab. **Amount Paid** is zero and
  **Amount Residual** is zero (both only become meaningful once the document is opened —
  see `05-approve`).
