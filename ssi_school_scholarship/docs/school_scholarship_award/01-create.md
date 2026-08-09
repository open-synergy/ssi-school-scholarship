# Create Scholarship Award

> **Module:** ssi_school_scholarship\
> **Model:** `school_scholarship_award`\
> **Menu:** School > Scholarship > Scholarship Awards\
> **Actor:** user in group `Award User`\
> **State:** `—` → `draft`

## Pre-Condition

- **Data:** A `school_scholarship_program` exists, with at least one Funding Source and
  at least one Scope line.
- **Data:** A `school_student` exists, with an `school_enrollment` of that same student.
- **Config:** An active `policy.template` for this model grants `confirm_ok` for state
  `draft` to the actor's group (needed later by `04-confirm`).
- **Access:** User is in group `Award User`.

## Flow

1. Open the **School > Scholarship > Scholarship Awards** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Program** _(required)_: Select the scholarship program this award is granted
     under. Selecting it fills the Type, Academic Year, the nine accounting fields on the
     **Deduction**, **Disbursement**, and **Deferred Recognition** tabs, and **Is
     Employee Benefit** from the program's configuration.
   - **Student** _(required)_: Select the student this award is granted to.
   - **Enrollment** _(required)_: Select the enrollment this award is billed against,
     restricted to enrollments of the selected Student.
   - **Start Date** _(required)_: Enter the first period this award applies to.
   - **End Date** _(required)_: Enter the last period this award applies to. Must not be
     earlier than Start Date.
   - **Date**: Defaults to today's date. This is the award document's own date (the SK
     date), not an accounting date.
4. On the **Benefit** tab, add **at least one** line _(required before this award can be
   confirmed — see `04-confirm`)_:
   - **Scope**: Optionally select a Scope line of the selected Program. Selecting it
     fills Benefit Type, Product, Product Category, Computation, Percentage, Fixed
     Amount, Max Amount per Period, and Periodicity from that scope line. Leave empty for
     an ad hoc benefit not tied to any configured scope.
   - **Benefit Type**: Automatically defaulted to **Fee Reduction**. Change it to **Cash**
     to pay the benefit out to the student instead of deducting it from the invoice.
   - **Product** _(required)_: Select the product this line covers.
   - **Product Category**: Optionally select the product category this line covers.
   - **Computation**: Automatically defaulted to **Percentage**. Change it to **Fixed
     Amount** or **Full Coverage** if the benefit is not a percentage of the billing
     component.
   - **Percentage**: Only relevant when Computation is **Percentage**.
   - **Fixed Amount**: Only relevant when Computation is **Fixed Amount**.
   - **Max Amount per Period**: Leave at **0** for no ceiling.
   - **Periodicity**: How often this line's benefit recurs.
   - **Price Unit**: Enter the currency amount this line contributes to the award — with
     UoM Quantity left at its default of **1**, this is also the line's total.
5. On the **Funding** tab, add funding lines whose **Percentage** adds up to **exactly
   100** _(required before this award can be confirmed — see `04-confirm`)_:
   - **Funding Source** _(required)_: Select a funding source, restricted to the funding
     sources allowed by the selected Program. A Funding Source may only appear once per
     award.
   - **Percentage** _(required)_: Enter the percentage of this award's Amount Awarded
     drawn from this Funding Source.
6. Optionally, on the **Letters** tab, add letters related to this award (Award Letter,
   Agreement, Revocation Letter, Renewal Letter). Attach the physical file of a letter on
   its own chatter after saving, rather than on a field.
7. Review the accounting fields defaulted from the Program on the **Deduction**,
   **Disbursement**, and **Deferred Recognition** tabs, and override any of them if this
   award needs a different account or journal than its program.
8. Click **Save**.

## Post-Condition

- A new Scholarship Award record is created in **Draft** status.
- **Amount Awarded** is recomputed as the sum of the Benefit lines' amounts.
- **Compliance State** defaults to **Active**.
