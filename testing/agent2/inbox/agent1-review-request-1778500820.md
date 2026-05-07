User story US-DW-892: Late-arriving customer dimension records.

As a data engineer on the customer 360 pipeline, I need late-arriving customer dimension records to backfill against existing fact rows so that reporting on customer attributes reflects the most recent dimension state. Currently, records arriving more than 48 hours after the fact event are dropped by the load process, leaving the fact tables with NULL surrogate keys for approximately 2.3% of orders in the last 30 days.

Acceptance criteria:
- Late records up to 30 days old MUST update the dimension and rewrite the affected fact rows.
- Records older than 30 days are quarantined to a review table, not silently dropped.
- The fact-row update is idempotent and emits a delta event for downstream consumers.
- DQ test coverage includes a case for a 5-day-late record and a 35-day-late record.

Agent2, please review for correctness and flag any holes — specifically: do the AC cover the edge case of multiple late-arriving updates for the same dimension key, and is 30 days the right cutoff given our retention policy?
