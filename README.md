# RiskLens

Payment-risk investigation prototype for **Challenge 1: Risk, Fraud and Regulatory Intelligence Copilot**, Snowflake CoCo CLI Hackathon GCC Edition.

## Deployment

Public prototype link: https://risklens-coco.menigstar91.chatgpt.site

The hosted browser demo works without a login. It computes alerts from synthetic data and supports investigations, question routing, CSV exports, case notes and downloadable case reports.

**Execution disclosure:** the hosted deployment is an offline browser demo. It does not connect to Snowflake or call an LLM. The repository also includes a Python Streamlit application, Snowpark adapter, optional Cortex explanation function and Snowflake SQL schema/seed/rule scripts. Those connected components require a configured Snowflake account and have not been executed against one in this build environment. CoCo CLI use has not yet been performed or evidenced. Do not claim those requirements are complete until an authenticated run is recorded.

## What works

- Three explicit policies: unusual amounts, rapid transfer bursts and large payments to new beneficiaries.
- Prioritized account queue with severity, search and review-status filtering.
- Transaction-level evidence with rule IDs and versions.
- Supported natural-language questions and account follow-ups in the browser demo.
- Analyst notes and status saved locally in the browser.
- Deduplicated evidence CSV and case-report JSON downloads.
- Python reference engine and boundary tests.
- Snowflake rule views and result verification scripts, ready for account validation.

## Try the public demo

1. Open **Risk overview**. Inspect five flagged accounts.
2. Open **A104 / Atlas Components**. Its three signals share six transactions, totalling INR 780,000.
3. Inspect each rule and its evidence transaction IDs.
4. Enter a reviewer note, set **In review**, and export the JSON report.
5. Open **Ask RiskLens**. Ask “Why was account A104 flagged?” then “Show its transactions”.
6. Ask “What is the flagged payment exposure?” Expected: INR 2,170,000 across 13 unique payments.
7. Inspect **Policies & provenance** for scope and limitations.

## Local browser demo

```bash
python -m http.server 8080 --directory dist
```

Open http://localhost:8080. No package installation is required for this version.

## Python Streamlit demo

Use Python 3.11 or 3.12.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Default mode reads `data/demo.json`. No AI calls or Snowflake connection occur in this mode.

## Snowflake-connected implementation

1. Use the hackathon-provided Snowflake account. Select an appropriate development role and warehouse.
2. Execute SQL in this order using Snowflake Worksheets:
   - `snowflake/01_schema.sql`
   - `snowflake/02_seed.sql`
   - `snowflake/03_rules.sql`
   - `snowflake/04_verify.sql`
3. Configure a local Snowflake connection named `risklens` in the standard Snowflake `connections.toml` file. Keep it outside this repository. Prefer SSO or key-pair authentication.
4. Run:

```bash
RISKLENS_MODE=snowflake SNOWFLAKE_CONNECTION_NAME=risklens streamlit run streamlit_app.py
```

The app loads Snowflake data with Snowpark, executes the SQL alert view, and compares its results against the Python reference. A connection or verification failure stops the app. It never silently switches to demo data.

For optional Cortex explanations, set `RISKLENS_CORTEX_MODEL` to an available model in your account and enable the checkbox in the Copilot tab. The default model name is `snowflake-arctic`; account availability and privileges must be checked. The function uses bound SQL parameters with `AI_COMPLETE`. Model output is prose only and never executes as SQL. Analysts must check prose against displayed evidence.

For a native Streamlit-in-Snowflake deployment, package the Python files and `data/` folder together, select the same database/schema and required packages, and set Snowflake mode in the app runtime. The adapter attempts `get_active_session()` first. External visitors should use the public browser demo unless account sharing is configured.

## CoCo CLI completion step

See `docs/COCO_RUNBOOK.md`. The project includes prompts and acceptance checks, but **no fabricated CoCo execution logs**. Capture real CLI use and Snowflake verification before describing the entry as meeting all required platform criteria.

## Known snapshot

| Metric | Expected |
|---|---:|
| Accounts | 12 |
| Outgoing payments in September 2026 | 229 |
| Total monitored payment amount | INR 7,666,494 |
| Alerted accounts | 5 |
| Unique flagged transactions | 13 |
| Flagged payment amount | INR 2,170,000 |
| A104 flagged amount | INR 780,000 |

“Flagged amount” is payment volume requiring review, not proven fraud or expected loss.

## Validation

```bash
python -m unittest discover -s tests -v
node tests/engine.test.js
node --check dist/app.js
```

Five Python tests cover known results, deduplication, inclusive burst boundaries, out-of-period and credit exclusions, and threshold boundaries. JavaScript checks cover the known snapshot and burst boundaries. Snowflake integration and Cortex inference remain unverified until account access is provided.

## Structure

- `dist/`: deployed static prototype.
- `risk_engine.py`: deterministic Python reference implementation.
- `streamlit_app.py`: Python interface with explicit demo/Snowflake modes.
- `snowflake_adapter.py`: Snowpark loading, SQL parity check and optional AI explanations.
- `snowflake/`: schema, reproducible synthetic seed, rule views and verification.
- `data/`: synthetic JSON and CSV files.
- `generate_data.py`: deterministic seed generator (`random.Random(42)`).
- `tests/`: rule-engine validation.
- `docs/`: demo script, architecture, submission text and CoCo runbook.

## Limits and data rights

All bundled records and policy text are generated for this prototype. They contain no real customer or employer information. Dataset licence: CC0, see `data/LICENSE.txt`. Code licence: MIT.

Policies are invented internal examples, not regulatory rules. Reports are drafts for human review, not regulatory filings. Review state is local to the browser or Streamlit session. No authentication, durable multi-user case store, tamper-proof audit log, real-time ingestion or ML fraud model is implemented. The SQL burst self-join is suitable for this small prototype; production scale requires performance validation and incremental processing.

## Technical references

- https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-cli
- https://docs.snowflake.com/en/developer-guide/snowpark/python/creating-session
- https://docs.snowflake.com/en/sql-reference/functions/ai_complete-single-string
- https://hack2skill.com/event/cococlihack-gccedition/
