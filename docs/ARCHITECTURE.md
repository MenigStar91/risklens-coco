# Architecture

## Public hosted MVP

Static HTML/CSS/JavaScript loads a bundled synthetic snapshot. `engine.js` applies versioned rules. The UI presents alerts, evidence, supported natural-language question routing, and reports. Browser localStorage holds notes and status. No server or credential is needed.

## Snowflake implementation provided in source

Snowflake tables hold accounts, transactions and policy text. `MONITORED_PAYMENTS` applies time, currency and direction scope. `SIGNAL_EVIDENCE` produces transaction/policy matches. `FLAGGED_PAYMENTS` deduplicates rows. `ACCOUNT_ALERTS` aggregates evidence and priority. The Snowpark adapter loads the snapshot and compares the SQL aggregates with the Python reference before rendering results.

Optional `AI_COMPLETE` receives bounded question text and selected case evidence via bound SQL parameters. The model produces a review explanation; it never generates executable SQL in this implementation. Reviewer inspection is required because prompt instructions alone cannot guarantee correctness.

## Rules

- POL-01: amount at least INR 200,000 and at least five times the declared account baseline.
- POL-02: at least four outgoing transfers inside an inclusive trailing 15-minute interval. Evidence includes every member of a qualifying window.
- POL-03: beneficiary age at transaction time at most seven days and amount at least INR 75,000.

High priority means at least two distinct rule types, or a flagged payment of at least INR 500,000. Other alerted accounts receive medium priority. This is a deterministic queue priority, not a statistical risk probability.

## Production considerations

The current demo does not implement tenant access, shared durable cases, real-time ingestion or a tamper-proof audit trail. For production, add role-scoped data access, durable review events with immutable event IDs, incremental pipelines, query budgets and evaluation on labelled data. The SQL burst self-join needs warehouse benchmarking at realistic scale. Policy/model versions and data snapshot identifiers should persist with every report.
