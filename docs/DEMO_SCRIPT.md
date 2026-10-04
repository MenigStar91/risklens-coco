# Three-minute prototype demonstration

**0:00–0:25 — Problem**
“RiskLens helps a payment-risk analyst inspect alerts and prepare an evidence-backed investigation draft. Our example uses entirely synthetic transactions and internal demo policies.”

**0:25–0:50 — Overview**
Show Risk overview. “We monitor 229 September payments. Five accounts trigger rules. Thirteen unique payments account for INR 2,170,000 flagged volume. We deduplicate transactions that match several rules.”

**0:50–1:35 — Investigation**
Open A104. “Atlas Components triggers unusual payment size, rapid repeated transfers, and large payments to a new beneficiary. These are review signals. We can inspect the exact rule, its version, and six underlying transactions.”

**1:35–2:00 — Analyst review**
Enter “Validate beneficiary onboarding and request invoice support.” Set In review. Export the case report. “The report carries evidence and policy references. A human records the assessment. This prototype stores review state locally.”

**2:00–2:35 — Questions**
Ask “Why was account A104 flagged?” Follow with “Show its transactions.” Ask “What is the flagged payment exposure?” Show calculated evidence and totals.

**2:35–3:00 — Architecture and limits**
“The public prototype runs deterministic analysis in the browser. We also provide a Python Streamlit implementation and Snowflake rule views with a parity check, plus optional Cortex explanations. Connected platform execution and CoCo usage require authenticated validation and are not claimed for this offline deployment.”

Only replace the final sentence after completing and documenting actual connected runs.
