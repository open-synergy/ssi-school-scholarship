.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============================================
School Scholarship Deduction - Operating Unit
=============================================

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


Work Instruction
=================

* `Create Scholarship Deduction <docs/school_scholarship_deduction/01-create.html>`_
* `Create Scholarship Deduction Recognition <docs/school_scholarship_deduction_recognition/01-create.html>`_


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/open-synergy/ssi-school-scholarship/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.


Credits
=======

Contributors
------------

* Andhitia Rama <andhitia.r@gmail.com>

Maintainer
----------

.. image:: https://simetri-sinergi.id/logo.png
   :alt: PT. Simetri Sinergi Indonesia
   :target: https://simetri-sinergi.id

This module is maintained by the PT. Simetri Sinergi Indonesia.
