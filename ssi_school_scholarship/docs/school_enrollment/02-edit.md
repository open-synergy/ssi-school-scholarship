# Edit Enrollment

> **Module:** `ssi_school_scholarship`\
> **Extends:** ssi_school — model `school_enrollment`, aksi `02-edit`

## Modified Validation

- **Compute Payment**, the **Copy Payment Term** wizard, and deleting a payment term row
  by hand will fail **if** a scholarship award has a Schedule line pinned to one of the
  payment terms being deleted. The award state does not matter.
- The error message names the payment term and the scholarship award that refers to it.
- To proceed, cancel the scholarship award first (see the scholarship award
  `10-cancel`), then recompute or delete the payment terms.
