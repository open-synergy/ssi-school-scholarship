# Create Scholarship Award

> **Module:** ssi_school_scholarship_operating_unit\
> **Extends:** ssi_school_scholarship — model `school_scholarship_award`, action
> `01-create`

## Additional Post-Condition

- **Operating Unit** (added by this module, hidden unless the _Multiple Operating Unit_
  group applies) is automatically set from the selected **Enrollment**'s School as soon
  as **Enrollment** is picked in the Flow, whenever that school belongs to exactly one
  operating unit. When the school belongs to zero or more than one operating unit,
  **Operating Unit** keeps its previous value (initially the current user's default
  operating unit) and is not overridden — it can still be changed manually.

## Modified — Record Visibility

- Users in the _Operating Unit_ group only see, edit, and delete Scholarship Award
  records whose Operating Unit matches one of their own Operating Units. Users outside
  this group are not restricted by this rule.
