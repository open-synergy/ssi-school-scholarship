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
- **Data:** At least one `product.product` or `product.category` exists, to scope the
  program's benefit to.
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
   - **Sequence**: Automatically defaulted to **5**. Change it to control the display
     order among Scholarship Programs within the same academic year — lower values
     appear first.
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
5. On the **Scope** tab, add **at least one** line _(required — the program is rejected
   on save without one)_:
   - **Scope Basis**: Automatically defaulted to **Product**. Change it to **Product
     Category** to cover an entire category of billing components instead of a single
     product.
   - **Product** _(required when Scope Basis is Product)_: Select the product this line
     covers.
   - **Product Category** _(required when Scope Basis is Product Category)_: Select the
     product category this line covers.
   - **Benefit Type**: Automatically defaulted to **Fee Reduction**. Change it to
     **Cash** to pay the benefit out to the student instead of deducting it from the
     invoice.
   - **Computation**: Automatically defaulted to **Percentage**. Change it to **Fixed
     Amount** or **Full Coverage** if the benefit is not a percentage of the billing
     component.
   - **Percentage** _(required above 0 and at most 100 when Computation is Percentage)_:
     Enter the percentage of the billing component this line covers.
   - **Fixed Amount**: Only relevant when Computation is **Fixed Amount**; enter the
     amount covered.
   - **Max Amount per Period**: Leave at **0** for no ceiling, or enter the maximum this
     line may cover in a single period.
   - **Periodicity**: Automatically defaulted to **Per Payment Term**. Fee Reduction
     lines cannot change this, since their deduction schedule is derived from the
     student's payment term.
6. Optionally, on the **Criteria** tab, add eligibility criteria checklist lines for the
   committee to review when deciding whether to award this program to an applicant:
   - **Criteria** _(required)_: Enter a short description of the criterion.
   - **Evaluation Method**: Automatically defaulted to **Manual**. Change it to
     **Domain** or **Python Code** if the criterion should be derived automatically —
     Domain requires the **Domain** field to be filled in, and Python Code requires the
     **Python Code** field to be filled in.
   - **Is Hard Requirement**: Check this if failing this criterion disqualifies the
     applicant outright.
   - **Weight**: Enter the relative weight of this criterion in the committee's scoring.
7. Review the accounting fields defaulted from the Scholarship Type on the
   **Deduction**, **Disbursement**, and **Deferred Recognition** tabs, and override any
   of them if this program needs a different account or journal than its type. On the
   **Deduction** tab, **Allow Asymmetric Recognition** may also be checked as an
   explicit opt-in for a foundation that intentionally defers the deduction/expense
   recognition of an award without deferring the related revenue recognition.
8. Optionally, on the **Description** tab, enter a description of this program.
9. Click **Generate Code** in the header to automatically assign a code from the
   `sequence.template` configured for `school_scholarship_program`. This requires an
   active `sequence.template` for this model — without one, the action fails with an
   error. You may also leave the Code field as **/** or type a code manually instead.
10. Click **Save**.

## Post-Condition

- A new Scholarship Program record is created and active.
- The new Scholarship Program becomes selectable wherever a scholarship program is
  required.
