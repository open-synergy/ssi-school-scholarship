.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============================
School Scholarship Deduction
=============================

Posts a scholarship deduction as its own journal entry -- debiting a discount
account per deduction line and crediting the student's receivable account on
the header -- then reconciles that credit against one or more open customer
invoices, so their residual drops and they move to Paid once fully covered.


Work Instruction
=================

Scholarship Deduction
-----------------------

* `Create Scholarship Deduction <docs/school_scholarship_deduction/01-create.html>`_
* `Confirm Scholarship Deduction <docs/school_scholarship_deduction/04-confirm.html>`_
* `Approve Scholarship Deduction <docs/school_scholarship_deduction/05-approve.html>`_
* `Create Due Recognition - Scholarship Deduction <docs/school_scholarship_deduction/06-create-due-recognition.html>`_
* `Cancel Scholarship Deduction <docs/school_scholarship_deduction/10-cancel.html>`_

Scholarship Award
-----------------------

* `Create Due Deduction - Scholarship Award <docs/school_scholarship_award/07-create-due-deduction.html>`_


Installation
============

To install this module, you need to:

1.  Clone the branch 14.0 of the repository https://github.com/open-synergy/ssi-school-scholarship
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list (Must be on developer mode)
4.  Go to menu *Apps -> Apps -> Main Apps*
5.  Search For *School Scholarship Deduction*
6.  Install the module


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
