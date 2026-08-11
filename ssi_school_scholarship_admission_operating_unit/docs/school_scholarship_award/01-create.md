# Create Scholarship Award

> **Module:** ssi_school_scholarship_admission_operating_unit\
> **Extends:** ssi_school_scholarship — model `school_scholarship_award`, action `01-create`

## Additional Post-Condition

- **Operating Unit** (added by `ssi_school_scholarship_operating_unit`, hidden unless
  the _Multiple Operating Unit_ group applies) is automatically set from the selected
  **Admission**'s School as soon as **Admission** is picked in the Flow — that is,
  whenever **Billing Source** is **Admission** — and that school belongs to exactly one
  operating unit. When the school belongs to zero or more than one operating unit,
  **Operating Unit** keeps its previous value and is not overridden — it can still be
  changed manually. The existing derivation from the Enrollment's School (added by
  `ssi_school_scholarship_operating_unit`, used when **Billing Source** is
  **Enrollment**) is unchanged.
