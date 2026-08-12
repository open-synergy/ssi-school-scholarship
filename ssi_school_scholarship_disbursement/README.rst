.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================================
School Scholarship Disbursement
=================================

Posts a cash scholarship disbursement as its own journal entry -- crediting the
student's payable account on the header and debiting each disbursement line's own
expense account -- then simply waits for an ``account.payment`` created outside this
document to be reconciled against it.


Work Instruction
=================

Scholarship Disbursement
-----------------------------

* `Create Scholarship Disbursement <docs/school_scholarship_disbursement/01-create.html>`_
* `Confirm Scholarship Disbursement <docs/school_scholarship_disbursement/04-confirm.html>`_
* `Approve Scholarship Disbursement <docs/school_scholarship_disbursement/05-approve.html>`_
* `Cancel Scholarship Disbursement <docs/school_scholarship_disbursement/10-cancel.html>`_

Scholarship Award
------------------------

* `Create Due Disbursement - Scholarship Award <docs/school_scholarship_award/08-create-due-disbursement.html>`_


Installation
============

To install this module, you need to:

1.  Clone the branch 14.0 of the repository https://github.com/open-synergy/ssi-school-scholarship
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list (Must be on developer mode)
4.  Go to menu *Apps -> Apps -> Main Apps*
5.  Search For *School Scholarship Disbursement*
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
