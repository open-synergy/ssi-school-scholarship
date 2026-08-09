# Generate Scholarship Award Schedule

> **Module:** ssi_school_scholarship\
> **Model:** `school_scholarship_award`\
> **Menu:** School > Scholarship > Scholarship Awards\
> **Actor:** user in group `Award User`\
> **Requires:** `05-approve`

## Pre-Condition

- **Record:** Status is **On Progress**.
- **Config:** An active `policy.template` for this model grants `generate_schedule_ok`
  for state `open` to the actor's group.
- **Access:** User is in group `Award User`.

## Flow

1. Open the **School > Scholarship > Scholarship Awards** menu.
2. Open an On Progress award.
3. Click the **Generate Schedule** button (`action_generate_schedule`).

## Post-Condition

- One Schedule line is created on the **Schedule** tab per eligible Benefit line/Payment
  Term (or Benefit line/period, for a Cash line) pairing not already scheduled. Lines
  already scheduled -- including any already **Realized** or manually overridden -- are
  left untouched.

> **Note:** A Schedule line is also created automatically, for every pairing eligible at
> that moment, the instant the award reaches **On Progress** -- see `05-approve`. This
> button exists so the schedule can be regenerated afterwards, e.g. once a new Benefit
> line or a new Payment Term becomes eligible.
