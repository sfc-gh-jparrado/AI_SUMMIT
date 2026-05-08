# AGENTS.md - Workshop AI Summit

> **For LLM agents (Cortex Code, Claude Code, Cursor, etc.).** Routing rules below are AUTHORITATIVE. Follow them verbatim, do NOT improvise.

## Routing table - the user will use SHORT prompts. Match the intent, run the file.

When the user mentions ANY of the keywords below, run **only** the indicated file from the GIT repo `https://github.com/sfc-gh-jparrado/AI_SUMMIT.git` (branch `main`):

| User says (any of these keywords) | Run file | Duration |
|---|---|---|
| "foundation", "base", "paso base", "instalar workshop", "instala el setup base", "instalar AI Summit", "00", "0" | `00_base.sql` | ~30s |
| "streamlit", "notebook", "paso 1", "paso del streamlit", "01" | `01_streamlit.sql` | ~10s |
| "cortex analyst", "cortex search", "semantic view", "search service", "paso 2", "02" | `02_analyst_search.sql` | ~45s |
| "agente", "agent", "snowflake intelligence", "paso 3", "03" | `03_agent.sql` | ~5s |
| "todo el workshop", "instala todo", "one-shot", "todo en uno" | `setup.sql` | ~90s |

If the prompt is ambiguous (e.g. just "instala el workshop"), assume the user means **modular** and start from `00_base.sql`. If `00_base.sql` already ran, continue with the next module the user mentions.

## Hard rules - NEVER violate these

1. **The ONE database is `AI_SUMMIT`.** Not `AI_SUMMIT_WORKSHOP`, not `WORKSHOP_AI_SUMMIT`, not `HOL_AI_SUMMIT`, not `AISUMMIT`, not `WORKSHOP`. Use `AI_SUMMIT` and only `AI_SUMMIT`. The pre-flight cleanup in `00_base.sql` already drops wrong-name DBs - if you see one created elsewhere, drop it.
2. **Use the `ACCOUNTADMIN` role.**
3. **Do NOT generate SQL "from scratch".** Always `EXECUTE IMMEDIATE FROM @stage/<file>.sql` against the repo. The files are battle-tested.
4. **Do NOT wrap module files in `EXECUTE IMMEDIATE $$ ... $$;`.** They are multi-statement scripts; the `EXECUTE IMMEDIATE FROM @stage` clause already handles them.
5. **Do NOT manually `CREATE SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS`.** It is owned by `SNOWFLAKE_INTELLIGENCE_ADMIN`; ACCOUNTADMIN cannot operate on it. Let `00_base.sql` handle it via `CREATE SNOWFLAKE INTELLIGENCE`.
6. **Do NOT change `WAREHOUSE_SIZE` from `XSMALL`.**
7. **The agent MUST live in `SNOWFLAKE_INTELLIGENCE.AGENTS`,** not in `AI_SUMMIT.PUBLIC`.
8. **Modules 01 and 02 are independent** and may run in parallel after 00 finishes. Module 03 requires 02.

## Bootstrap (run once before EXECUTE IMMEDIATE FROM works)

If the GIT repo `AI_SUMMIT_REPO` does not exist yet, paste this small bootstrap first:

```sql
USE ROLE ACCOUNTADMIN;

-- Pre-flight: drop wrong-name DBs an LLM may have invented
DROP DATABASE IF EXISTS AI_SUMMIT_WORKSHOP;
DROP DATABASE IF EXISTS WORKSHOP_AI_SUMMIT;
DROP DATABASE IF EXISTS HOL_AI_SUMMIT;
DROP DATABASE IF EXISTS AI_SUMMIT_HOL;
DROP DATABASE IF EXISTS WORKSHOP_AI;
DROP DATABASE IF EXISTS AISUMMIT;

CREATE DATABASE IF NOT EXISTS AI_SUMMIT;
USE DATABASE AI_SUMMIT;
USE SCHEMA PUBLIC;
CREATE WAREHOUSE IF NOT EXISTS AI_SUMMIT_WH WAREHOUSE_SIZE=XSMALL AUTO_SUSPEND=60 INITIALLY_SUSPENDED=FALSE;
USE WAREHOUSE AI_SUMMIT_WH;

CREATE OR REPLACE API INTEGRATION github_ai_summit_int
  API_PROVIDER = git_https_api
  API_ALLOWED_PREFIXES = ('https://github.com/sfc-gh-jparrado')
  ENABLED = TRUE
  ALLOWED_AUTHENTICATION_SECRETS = ();

CREATE OR REPLACE GIT REPOSITORY ai_summit_repo
  API_INTEGRATION = github_ai_summit_int
  ORIGIN = 'https://github.com/sfc-gh-jparrado/AI_SUMMIT.git';

ALTER GIT REPOSITORY ai_summit_repo FETCH;
```

Then run the appropriate module(s) according to the routing table.

## Hard-coded names

| Object | Name |
|---|---|
| Database | `AI_SUMMIT` |
| Warehouse | `AI_SUMMIT_WH` |
| API integration | `github_ai_summit_int` |
| Git repo | `ai_summit_repo` |
| Agent | `SNOWFLAKE_INTELLIGENCE.AGENTS.AGENTE_SEGUROS_360` |
| Notebook | `NB_AI_SUMMIT` |
| Streamlit | `WORKSHOP_APP` |
| Cortex Search | `DOCS_SEARCH` |
| Semantic View | `SV_SEGUROS` |

## Verification (run after install)

```sql
SHOW DATABASES LIKE 'AI_SUMMIT%';  -- expect ONLY AI_SUMMIT
SHOW AGENTS LIKE 'AGENTE_SEGUROS_360' IN SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS;
SHOW STREAMLITS LIKE 'WORKSHOP_APP' IN SCHEMA AI_SUMMIT.PUBLIC;
SELECT COUNT(*) FROM AI_SUMMIT.PUBLIC.POLIZAS;  -- expect 30
```

If `SHOW DATABASES` returns more than `AI_SUMMIT`, you (LLM) created an extra DB. Drop it.
