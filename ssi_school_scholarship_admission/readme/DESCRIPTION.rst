Glue module that lets a School Scholarship Award be billed against a
``school_admission`` instead of only a ``school_enrollment``. Adds
``admission`` as a second Billing Source value, and derives the award's
School/Grade/Student and realization schedule from the selected
Admission's own payment terms once it has a School Student (created with
Create Student Profile, or when it reaches state Open). Also adds
Scholarship Amount and an Awards smart button to the Admission form,
mirroring what the base module already shows on Enrollment.
