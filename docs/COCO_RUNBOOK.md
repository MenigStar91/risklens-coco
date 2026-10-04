# CoCo CLI runbook

Status: prepared, not executed. Do not submit this document as proof of actual CoCo usage.

1. Install CoCo CLI using the official guide: https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-cli
2. Authenticate the hackathon Snowflake account and select the development role and warehouse.
3. Open a CoCo session from the repository directory.
4. Use the following prompts. Inspect any proposed changes before execution.

## Prompt 1: deploy and verify data

> Inspect README.md and the SQL files in snowflake/. We are building a synthetic payment-risk investigation copilot. Use the configured Snowflake account and existing development warehouse. Run the schema, seed and rules scripts in order in the dedicated RISKLENS.DEMO schema. The seed replaces data only in the dedicated demo tables. Run 04_verify.sql and report the actual results, query IDs and any failures. Do not claim success without executing the checks. Do not access other databases or customer data.

## Prompt 2: inspect rule correctness

> Compare snowflake/03_rules.sql with risk_engine.py and dist/engine.js. Verify a four-payment inclusive 15-minute burst, boundary amount thresholds, currency and time filters, and deduplication of overlapping policy signals. Run the existing local tests. Explain any differences and fix only confirmed defects.

## Prompt 3: connected app verification

> Launch streamlit_app.py in Snowflake mode using the configured local connection. Confirm the ACCOUNT_ALERTS SQL results match the Python reference. Verify A104 has six evidence rows and INR 780,000 flagged amount. If an available Cortex model and privileges are present, test an evidence-grounded explanation with AI_COMPLETE and confirm its transaction and policy citations. Capture actual results and limitations without exposing credentials.

## Evidence to retain

- Screenshot of CoCo session with relevant prompts and completed actions.
- Snowflake verification output and query IDs.
- Screenshot showing Streamlit “Connected to Snowflake” status.
- Optional Cortex response with its evidence references.
- Brief usage summary covering what CoCo actually changed or verified.

Never commit access tokens, connection files, passwords or secrets. Current public browser demo remains an offline demonstration even after a separate connected app run.
