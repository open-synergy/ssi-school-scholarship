# Create Scholarship Award

> **Module:** `ssi_school_scholarship_admission`\
> **Extends:** ssi_school_scholarship — model `school_scholarship_award`, action `01-create`

## Additional Fields

When this module is installed, **Billing Source** gains a second value:

- **Billing Source**: now also offers **Admission**, alongside the base module's
  **Enrollment**.
- **Admission** _(required when Billing Source is Admission)_: Select the admission this
  award is billed against, restricted to admissions that already have a School Student
  (created with **Create Student Profile** on the Admission, or automatically when the
  admission is **Open**) and are not **Cancelled** or **Rejected**. An admission without
  a School Student is not offered. Hidden when Billing Source is not Admission.
  Selecting it fills **Student** from the admission's School Student, and
  **School**/**Grade** from the admission.

## Related Views

- The **Awards** stat button in the button box of the Admission form
  (`action_open_scholarship_award`) opens the list of Scholarship Award records billed
  against that Admission. It only returns an `act_window` and writes no field, so it is
  pure navigation: informational only, not documented as an IK step or tour of its own.
