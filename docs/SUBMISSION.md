# Submission copy

## Project title
RiskLens — Payment Risk Investigation Copilot

## Challenge
Risk, Fraud and Regulatory Intelligence Copilot

## Summary
RiskLens helps financial operations analysts investigate suspicious-payment signals using transaction evidence and explicit monitoring policies. The prototype flags unusually large payments, rapid transfer bursts, and large payments to newly added beneficiaries. Analysts can ask supported questions, inspect transaction rows, record a review status and notes, and export investigation drafts with policy references. The dataset contains 229 synthetic outgoing payments across 12 accounts. The rule engine identifies five accounts and 13 unique flagged transactions, with overlapping alerts deduplicated.

## Implementation status
The public MVP is a working offline browser demo with deterministic question routing. The repository includes a Python Streamlit application, Snowpark integration, Snowflake SQL rule views and an optional Cortex explanation function. Snowflake-connected execution and CoCo CLI use still require authenticated validation. The deployed preview does not make live Snowflake or LLM calls.

## Differentiator
Every signal links to exact evidence transaction IDs and a versioned policy. Shared evidence counts once in payment exposure, and unsupported questions receive an explicit limitation. Analyst review remains separate from automated signals.

## Source code
https://github.com/MenigStar91/risklens-coco

## Prototype link
https://risklens-coco.menigstar91.chatgpt.site

## Data
Synthetic, deterministic seed generated for the project. Data licence: CC0. Code licence: MIT.

## Future work
Authenticated Snowflake deployment, documented CoCo execution, durable case review and audit history, evaluated natural-language query generation, incremental ingestion and larger-scale SQL performance testing.
