# Create Scholarship Type

> **Module:** ssi_school_scholarship\
> **Model:** `school_scholarship_type`\
> **Menu:** School > Scholarship > Configuration > Scholarship Types\
> **Actor:** user in group `Scholarship Type`\
> **Inline Actions:** `action_generate_code` (Generate Code)

## Pre-Condition

- **Data:** An `account.journal` exists to be selected as the Deduction Journal (must not
  be of type Cash or Bank).
- **Data:** An `account.account` exists to be selected as the Discount Account (must not
  be a reconcilable account).
- **Access:** User is in group `Scholarship Type`.

## Flow

1. Open the **School > Scholarship > Configuration > Scholarship Types** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Name** _(required)_: Enter the name of the scholarship type (e.g. "Full
     Scholarship", "Staff Child Tuition Relief").
   - **Code** _(required)_: Enter a unique code identifying this scholarship type, or
     enter **/** to assign it later using **Generate Code**.
   - **Sequence**: Automatically defaulted to **5**. Change it to control the display
     order among Scholarship Types — lower values appear first.
4. On the **Deduction** tab, fill in:
   - **Deduction Journal** _(required)_: Select the journal used to post the scholarship
     deduction entry. It must not be of type Cash or Bank.
   - **Discount Account** _(required)_: Select the contra-revenue account the deduction is
     booked to. It must not be a reconcilable account.
   - **Is Employee Benefit**: Leave unchecked unless this scholarship type is granted as an
     employee benefit.
   - **Employee Benefit Account**: Only needed when **Is Employee Benefit** is checked.
   - **Deduction Product**: Optionally select the product used to mark the deduction line
     on the student invoice.
5. Optionally, on the **Disbursement** tab, fill in the **Disbursement Journal**,
   **Expense Account**, and **Payable Account** used when the scholarship is paid out in
   cash instead of deducted from the invoice.
6. Optionally, on the **Deferred Recognition** tab, fill in the **Deferred Discount
   Account**, **Deferred Expense Account**, and **Recognition Journal** used to defer and
   later recognise the discount or expense across periods.
7. Click **Generate Code** in the header to automatically assign a code from the
   `sequence.template` configured for `school_scholarship_type`. This requires an active
   `sequence.template` for this model — without one, the action fails with an error. You
   may also leave the Code field as **/** or type a code manually instead.
8. Click **Save**.

## Post-Condition

- A new Scholarship Type record is created and active.
- The new Scholarship Type becomes selectable wherever a scholarship type is required.
