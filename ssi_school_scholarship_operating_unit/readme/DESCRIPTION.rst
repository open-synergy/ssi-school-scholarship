Glue module that adds Operating Unit support to the School Scholarship
module. Extends ``school_scholarship_type``,
``school_scholarship_funding_source``, and ``school_scholarship_program``
with ``mixin.multiple_operating_unit``, and ``school_scholarship_award``
with ``mixin.single_operating_unit``. The award's ``operating_unit_id`` is
automatically derived from the school of its selected Enrollment whenever
that school belongs to exactly one Operating Unit. Adds the matching
security groups, record rules, and view integration for all four models.
