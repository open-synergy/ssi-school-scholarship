# Cancel Admission

> **Module:** `ssi_school_scholarship_admission`\
> **Extends:** ssi_school_admission — model `school_admission`, aksi `10-cancel`

## Modified Validation

- Cancelling an admission will fail **if** a scholarship award sourced from that
  admission is still active, that is, its status is **Draft**, **Waiting for Approval**,
  **On Progress**, or **Done**.
- The error message names the active scholarship award.
- To proceed, cancel (or reject) the scholarship award first, then cancel the admission.
  An award that is already **Cancelled** or **Rejected** does not block cancellation.
