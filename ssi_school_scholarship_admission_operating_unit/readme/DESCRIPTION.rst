Glue module that adds Operating Unit support to Admission-sourced Scholarship
Awards. Extends ``school_scholarship_award`` so an award billed against an
Admission (``source_type`` **Admission**, added by
``ssi_school_scholarship_admission``) also has its ``operating_unit_id``
automatically derived from the school of its selected Admission whenever
that school belongs to exactly one Operating Unit -- the same rule
``ssi_school_scholarship_operating_unit`` already applies to
Enrollment-sourced awards. Adds no new model, menu, security group, or
access rule of its own.
