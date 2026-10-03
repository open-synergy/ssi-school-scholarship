# Cancel Enrollment

> **Module:** `ssi_school_scholarship`\
> **Extends:** ssi_school — model `school_enrollment`, aksi `10-cancel`

## Modified Validation

- Cancelling an enrollment will fail **if** a scholarship award sourced from that
  enrollment is still active, that is, its status is **Draft**, **Waiting for
  Approval**, **On Progress**, or **Done**.
- The error message names the active scholarship award.
- To proceed, cancel (or reject) the scholarship award first, then cancel the
  enrollment. An award that is already **Cancelled** or **Rejected** does not block
  cancellation.
