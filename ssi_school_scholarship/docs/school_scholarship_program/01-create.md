# Create Scholarship Program

> **Module:** ssi_school_scholarship\
> **Model:** `school_scholarship_program`\
> **Menu:** School > Scholarship > Configuration > Scholarship Programs\
> **Actor:** user in group `Scholarship Program`\
> **Inline Actions:** `action_generate_code` (Generate Code)

## Pre-Condition

- **Data:** A `school_scholarship_type` exists, to default the accounting fields from.
- **Data:** A `school` and a `school_academic_year` exist.
- **Data:** At least one `school_scholarship_funding_source` exists, to fund awards
  granted under this program.
- **Access:** User is in group `Scholarship Program`.

## Flow

1. Open the **School > Scholarship > Configuration > Scholarship Programs** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Name** _(required)_: Enter the name of the program (e.g. "2026/2027 Need-Based
     Scholarship").
   - **Code** _(required)_: Enter a unique code identifying this program, or enter **/**
     to assign it later using **Generate Code**.
   - **Scholarship Type** _(required)_: Select the `school_scholarship_type` this
     program follows. Selecting it fills the Deduction Journal, Discount Account, Is
     Employee Benefit, Employee Benefit Account, Disbursement Journal, Expense Account,
     Payable Account, Deferred Discount Account, Deferred Expense Account, and
     Recognition Journal fields on the Deduction, Disbursement, and Deferred Recognition
     tabs from the type's configuration.
   - **School** _(required)_: Select the school this program applies to.
   - **Academic Year** _(required)_: Select the academic year this program applies to.
   - **Funding Basis**: Automatically defaulted to **Need Based**. Change it to **Merit
     Based**, **Hybrid**, or **Categorical** if this program grants scholarships on a
     different basis.
4. On the **Eligibility** tab, fill in:
   - **Grades**: Optionally select the grades eligible for this program. Leave empty to
     make every grade eligible.
   - **Funding Sources** _(required)_: Select the Scholarship Funding Source(s) an award
     granted under this program may draw from.
   - **Quota**: Leave at **0** for no quota, or enter the maximum number of awards this
     program may grant.
   - **Is Renewable**: Check this if an award granted under this program may be renewed
     into a following academic year.
   - **Max Renewal**: Only relevant when **Is Renewable** is checked; enter the maximum
     number of times an award may be renewed.
5. Review the accounting fields defaulted from the Scholarship Type on the
   **Deduction**, **Disbursement**, and **Deferred Recognition** tabs, and override any
   of them if this program needs a different account or journal than its type. On the
   **Deduction** tab, **Allow Asymmetric Recognition** may also be checked as an
   explicit opt-in for a foundation that intentionally defers the deduction/expense
   recognition of an award without deferring the related revenue recognition.
6. Optionally, on the **Description** tab, enter a description of this program.
7. Click **Generate Code** in the header to automatically assign a code from the
   `sequence.template` configured for `school_scholarship_program`. This requires an
   active `sequence.template` for this model — without one, the action fails with an
   error. You may also leave the Code field as **/** or type a code manually instead.
8. Click **Save**.

## Post-Condition

- A new Scholarship Program record is created and active.
- The new Scholarship Program becomes selectable wherever a scholarship program is
  required.
