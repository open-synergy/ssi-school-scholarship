# Create Scholarship Funding Source

> **Module:** ssi_school_scholarship_donation\
> **Extends:** ssi_school_scholarship — model `school_scholarship_funding_source`, action
> `01-create`

## Additional Pre-Condition

- **Data:** A `donation_fund` exists, bound to the same `account.analytic.account` as
  this Funding Source, if this Funding Source is to draw from a Donation Fund.

## Additional Fields

When this module is installed, the create form gains one optional field:

- **Donation Fund**: Select the `donation_fund` this Funding Source draws its committed
  and realized money from. Only a Donation Fund bound to the same Analytic Account as
  this Funding Source may be selected — saving with a mismatched Donation Fund is
  rejected with an error. Leave empty when this Funding Source does not draw from any
  Donation Fund.

## Additional Post-Condition

- Saving with a Donation Fund selected creates one `donation_fund_usage` ledger row, and
  `donation_fund.amount_committed`/`amount_realized`/`amount_available` on the selected
  Donation Fund start reflecting this Funding Source's own committed/realized amounts.
  Clearing the Donation Fund removes that ledger row.
