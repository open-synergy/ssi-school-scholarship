# Create Scholarship Funding Source

> **Module:** ssi_school_scholarship\
> **Model:** `school_scholarship_funding_source`\
> **Menu:** School > Configuration > Scholarship > Scholarship Funding Sources\
> **Actor:** user in group `Scholarship Funding Source`\
> **Inline Actions:** `action_generate_code` (Generate Code)

## Pre-Condition

- **Data:** An `account.analytic.account` exists to bind this funding source to, and is
  not yet bound to another Scholarship Funding Source.
- **Data:** A `school` and a `school_academic_year` exist, if this funding source is to
  be earmarked for a specific school or academic year.
- **Access:** User is in group `Scholarship Funding Source`.

## Flow

1. Open the **School > Configuration > Scholarship > Scholarship Funding Sources** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Name** _(required)_: Enter the name of the funding source (e.g. "Foundation Grant
     2026", "Alumni Donation Pool").
   - **Code** _(required)_: Enter a unique code identifying this funding source, or
     enter **/** to assign it later using **Generate Code**.
   - **Analytic Account** _(required)_: Select the `account.analytic.account` this
     funding source is bound to. An analytic account already bound to another
     Scholarship Funding Source cannot be selected again.
4. Optionally, select the **School** and **Academic Year** to earmark this funding
   source. Leave either empty to make it shared across every school or academic year.
5. Optionally, fill in the **Ceiling** to cap the total amount this funding source may
   disburse. Leave it at **0.00** for no ceiling.
6. Click **Generate Code** in the header to automatically assign a code from the
   `sequence.template` configured for `school_scholarship_funding_source`. This requires
   an active `sequence.template` for this model — without one, the action fails with an
   error. You may also leave the Code field as **/** or type a code manually instead.
7. Click **Save**.

## Post-Condition

- A new Scholarship Funding Source record is created and active.
- The new Scholarship Funding Source becomes selectable as a Funding Source on
  Scholarship Programs.
