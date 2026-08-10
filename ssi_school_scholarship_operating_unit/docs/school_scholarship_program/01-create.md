# Create Scholarship Program

> **Module:** ssi_school_scholarship_operating_unit\
> **Extends:** ssi_school_scholarship — model `school_scholarship_program`, action
> `01-create`

## Additional Fields

When this module is installed, the create form gains one optional field:

- **Operating Unit**: Select the operating unit(s) this Program belongs to. Leave empty
  to make the record visible to every operating unit. Only visible to users in the
  _Multiple Operating Unit_ group.

## Modified — Record Visibility

- The Program list is filtered by a record rule: a user only sees records that have no
  Operating Unit set, or that share at least one Operating Unit with their own Operating
  Units. This rule only restricts what a user can see — it does not restrict who can
  create, edit, or delete records.
