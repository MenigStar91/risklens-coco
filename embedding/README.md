# Live Snowflake embedding

Prepared implementation; not yet deployed or connected.

Keep the existing RISKLENS.DEMO.RISKLENS_LIVE object and database. First run
`snowflake/06_embedding_preflight.sql`. Check compute pool availability and
existing embedding domains before changing account settings.

Container source is in `native_container/`: it uses Streamlit's per-session
Snowflake connection and the same fully qualified live views. No data is copied
to the host. Empty dependencies use the container's preinstalled packages.
Public-demo Cortex inference is disabled to avoid visitor-triggered model costs.

The host must authenticate visitors before `handleEmbedRequest` (Sites can use
ChatGPT sign-in; no Snowflake account is required). Snowflake explicitly requires
an authenticated minting endpoint. Preserve existing allowed embedding origins
when adding https://risklens-coco.menigstar91.chatgpt.site.

Create a dedicated SERVICE user RISKLENS_EMBED_SVC and role
RISKLENS_EMBED_MINTER. Grant only USAGE on RISKLENS, RISKLENS.DEMO and
RISKLENS.DEMO.RISKLENS_LIVE, plus EMBED on that app. Assign the role to the
service user. Register an RSA public key on the service user; store the private
key as a hosted runtime secret, never in GitHub or chat.

Server-only runtime settings:

- SNOWFLAKE_ACCOUNT_URL=https://zdwluhm-zf39170.snowflakecomputing.com
- SNOWFLAKE_ACCOUNT=ZDWLUHM-ZF39170
- SNOWFLAKE_USER=RISKLENS_EMBED_SVC
- SNOWFLAKE_ROLE=RISKLENS_EMBED_MINTER
- STREAMLIT_APP=RISKLENS.DEMO.RISKLENS_LIVE
- PARENT_ORIGIN=https://risklens-coco.menigstar91.chatgpt.site
- SNOWFLAKE_PRIVATE_KEY=<PEM runtime secret>

The host calls POST /api/embed-url once per viewer session. Render the returned
URL in an iframe; never cache, log or reuse it. Permit downloads if sandboxing
the iframe. Every embedded viewer sees the same synthetic demo dataset.

Migration requires a supported compute pool, container source replacement,
RUNTIME_NAME=SYSTEM$ST_CONTAINER_RUNTIME_PY3_11 and the existing query warehouse.
Publish and verify before host activation. Rollback restores native/ source and
SYSTEM$WAREHOUSE_RUNTIME. Do not run the old deployment script after migration:
it explicitly switches the app back to the warehouse runtime.

Official reference:
https://docs.snowflake.com/en/developer-guide/streamlit/features/embedding/external-users
