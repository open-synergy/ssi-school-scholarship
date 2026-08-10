Glue module that adds Operating Unit support to the School Scholarship
Deduction module. Extends ``school_scholarship_deduction`` and
``school_scholarship_deduction_recognition`` with
``mixin.single_operating_unit``. The deduction's ``operating_unit_id`` is
derived from the selected Award's own Operating Unit; the recognition's is
derived from its parent Deduction's own Operating Unit. Both propagate their
Operating Unit to the ``account.move`` (and its lines) they create, and an
Allocation line targeting a Customer Invoice from a different Operating Unit
is rejected before any journal entry is created. Adds the matching security
groups, record rules, and view integration for both models.
