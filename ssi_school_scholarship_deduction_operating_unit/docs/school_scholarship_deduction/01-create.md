# Create Scholarship Deduction

> **Module:** ssi_school_scholarship_deduction_operating_unit\
> **Extends:** ssi_school_scholarship_deduction — model `school_scholarship_deduction`, action
> `01-create`

## Additional Post-Condition

- **Operating Unit** (added by this module, hidden unless the _Multiple Operating Unit_
  group applies) is automatically set from the selected **Award**'s own Operating Unit
  as soon as **Award** is picked in the Flow. It mirrors the Award's Operating Unit
  exactly -- when the Award has no Operating Unit, the field keeps its previous value
  (initially the current user's default operating unit) and is not overridden. It can
  still be changed manually.

## Modified — Record Visibility

- Users in the _Operating Unit_ group only see, edit, and delete Scholarship Deduction
  records whose Operating Unit matches one of their own Operating Units. Users outside
  this group are not restricted by this rule.
