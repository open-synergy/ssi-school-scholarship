Glue module that adds Operating Unit support to the School Scholarship
Disbursement module. Extends ``school_scholarship_disbursement`` with
``mixin.single_operating_unit``. Its ``operating_unit_id`` is derived from
the selected Award's own Operating Unit, and is propagated to the
``account.move`` (and its lines) this document creates. Adds the matching
security group, record rule, and view integration.
