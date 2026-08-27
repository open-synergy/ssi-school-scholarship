Glue module that lets a School Scholarship Funding Source draw its committed and
realized money from a ``donation_fund``. Adds an optional Donation Fund field to
Funding Source, keeps a ``donation_fund_usage`` ledger row for each Funding Source
that uses one, and forbids binding to a Donation Fund whose Analytic Account does
not match the Funding Source's own.
