# Create Scholarship Deduction

> **Module:** ssi_school_scholarship_deduction\
> **Model:** `school_scholarship_deduction`\
> **Menu:** School > Scholarship > Scholarship Deductions\
> **Actor:** user in group `Deduction User`\
> **State:** `—` → `draft`

## Pre-Condition

- **Data:** A `school_scholarship_award` exists, already `open`, with at least one
  Schedule line (state `scheduled`) and at least one Funding line.
- **Data:** An open `customer_invoice` exists, billed to the Award's own Partner, with a
  positive residual.
- **Config:** An active `policy.template` for this model grants `confirm_ok` for state
  `draft` to the actor's group (needed later by `04-confirm`).
- **Access:** User is in group `Deduction User`.

## Flow

1. Open the **School > Scholarship > Scholarship Deductions** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Award** _(required)_: Select the scholarship award this deduction realizes.
   - **Date**: Defaults to today's date.
   - On the **Accounting** tab:
     - **Journal** _(required)_: Select the accounting journal this document posts to.
     - **Receivable Account** _(required)_: Select the receivable account this document
       credits. Must be identical to the Receivable Account of every invoice allocated
       below, or opening this document is rejected (see `05-approve`).
4. On the **Lines** tab, add **at least one** line:
   - **Schedule** _(required)_: Select an Award Schedule line, restricted to the
     selected Award's own Schedule. Selecting it fills Description, Product, and Final
     Account from the Schedule line's Benefit.
   - **Funding** _(required)_: Select an Award Funding line, restricted to the selected
     Award's own Funding. Selecting it, together with Schedule, fills **Price Unit** as
     the Schedule line's Amount Planned multiplied by the Funding line's Percentage.
   - **UoM Quantity**: Left at its default of **1** — Price Unit is also this line's
     total.
5. On the **Allocations** tab, add **at least one** line:
   - **Customer Invoice** _(required)_: Select an open invoice, restricted to invoices
     of the selected Award's own Partner with a positive residual. Selecting it fills
     Invoice Residual and Invoice Receivable Account for reference, and defaults this
     document's own Receivable Account above when it is still empty.
   - **Amount Allocated** _(required)_: Enter the amount of this document applied to the
     selected invoice. Must not exceed Invoice Residual.
   - The sum of every Allocation line's Amount Allocated must equal the sum of the Lines
     tab's Price Subtotal (**Amount Unallocated** must reach zero) before this document
     can be opened — see `05-approve`.
6. Click **Save**.

## Post-Condition

- A new Scholarship Deduction record is created in **Draft** status.
- **Amount Total**, **Amount Allocated**, and **Amount Unallocated** are recomputed from
  the Lines and Allocations tabs.
