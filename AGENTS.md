# AGENTS.md - Workshop AI Summit

> **This file is for LLM agents (Cortex Code, Claude Code, Cursor, etc.).**
> If a user asks to install, deploy, or set up the "AI Summit" workshop / "Workshop AI Summit" / "HOL AI Summit", follow these instructions **verbatim**. Do NOT improvise.

## CRITICAL - Database name policy (read this first)

**The ONLY database the user wants is `AI_SUMMIT`.** No other names. No translations.

Before doing anything else, run this exact pre-flight script:

```sql
USE ROLE ACCOUNTADMIN;

-- Drop any database that an LLM may have invented from natural language
DROP DATABASE IF EXISTS AI_SUMMIT_WORKSHOP;
DROP DATABASE IF EXISTS WORKSHOP_AI_SUMMIT;
DROP DATABASE IF EXISTS HOL_AI_SUMMIT;
DROP DATABASE IF EXISTS AI_SUMMIT_HOL;
DROP DATABASE IF EXISTS WORKSHOP_AI;
DROP DATABASE IF EXISTS AISUMMIT;
DROP DATABASE IF EXISTS WORKSHOP;
```

**Rule:** if you (LLM) feel tempted to create a database with any name other than `AI_SUMMIT`, STOP. Use `AI_SUMMIT` and only `AI_SUMMIT`.

## Authoritative install procedure - PREFER THE MODULAR PATH

The repo is split into **4 ordered SQL modules**. Execute them in order. Each is idempotent and self-documenting.

| Step | File | Duration | Depends on |
|---|---|---|---|
| 0 | `00_base.sql` | ~30s | nothing |
| 1 | `01_streamlit.sql` | ~10s | step 0 |
| 2 | `02_analyst_search.sql` | ~45s | step 0 |
| 3 | `03_agent.sql` | ~5s | steps 0 + 2 |

Steps 1 and 2 are **independent** and may run in parallel after step 0 finishes.

### Bootstrap the GIT repo first (only needed once)

```sql
USE ROLE ACCOUNTADMIN;

-- Pre-flight cleanup
DROP DATABASE IF EXISTS AI_SUMMIT_WORKSHOP;
DROP DATABASE IF EXISTS WORKSHOP_AI_SUMMIT;
DROP DATABASE IF EXISTS HOL_AI_SUMMIT;

-- Minimal scaffolding so we can EXECUTE IMMEDIATE FROM the repo
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

### Then run the 4 modules

```sql
-- Step 0 (foundation): DB context, stages, data, tables
EXECUTE IMMEDIATE FROM @AI_SUMMIT.PUBLIC.AI_SUMMIT_REPO/branches/main/00_base.sql;

-- Step 1 (Streamlit + Notebook) - CAN run in parallel with step 2
EXECUTE IMMEDIATE FROM @AI_SUMMIT.PUBLIC.AI_SUMMIT_REPO/branches/main/01_streamlit.sql;

-- Step 2 (Cortex Analyst + Cortex Search) - CAN run in parallel with step 1
EXECUTE IMMEDIATE FROM @AI_SUMMIT.PUBLIC.AI_SUMMIT_REPO/branches/main/02_analyst_search.sql;

-- Step 3 (Snowflake Intelligence Agent) - REQUIRES step 2
EXECUTE IMMEDIATE FROM @AI_SUMMIT.PUBLIC.AI_SUMMIT_REPO/branches/main/03_agent.sql;
```

### One-shot alternative

`setup.sql` at the repo root chains all 4 modules in order. Use it if the user wants a single paste:

```sql
EXECUTE IMMEDIATE FROM @AI_SUMMIT.PUBLIC.AI_SUMMIT_REPO/branches/main/setup.sql;
```

## Hard-coded names (DO NOT modify)

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
SHOW NOTEBOOKS LIKE 'NB_AI_SUMMIT' IN SCHEMA AI_SUMMIT.PUBLIC;
SHOW STREAMLITS LIKE 'WORKSHOP_APP' IN SCHEMA AI_SUMMIT.PUBLIC;
SELECT COUNT(*) FROM AI_SUMMIT.PUBLIC.POLIZAS;  -- expect 30
```

## Things NOT to do

- Do NOT create any database with a name OTHER than `AI_SUMMIT`. No `AI_SUMMIT_WORKSHOP`, no `WORKSHOP_AI_SUMMIT`, no `HOL_AI_SUMMIT`. Use `AI_SUMMIT`.
- Do NOT translate "Workshop AI Summit" into a database identifier.
- Do NOT generate alternative SQL "from scratch". Always run the modules in the repo.
- Do NOT change `WAREHOUSE_SIZE` from `XSMALL`.
- Do NOT skip `ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION'` (handled by `00_base.sql`).
- Do NOT create the agent in `AI_SUMMIT.PUBLIC` - it must be in `SNOWFLAKE_INTELLIGENCE.AGENTS`.
- Do NOT wrap any of the module files in an extra `EXECUTE IMMEDIATE $$ ... $$;` block. The modules are multi-statement scripts and the EXECUTE IMMEDIATE FROM @stage clause already handles them correctly.
- Do NOT manually `CREATE SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS` - that schema is owned by `SNOWFLAKE_INTELLIGENCE_ADMIN` and `ACCOUNTADMIN` cannot operate on it. Let `CREATE SNOWFLAKE INTELLIGENCE` (in `00_base.sql`) provision it.

## Self-check before responding to user

After execution, verify only ONE workshop database exists:

```sql
SELECT COUNT(*) AS workshop_dbs FROM SNOWFLAKE.INFORMATION_SCHEMA.DATABASES
WHERE DATABASE_NAME LIKE 'AI_SUMMIT%' OR DATABASE_NAME LIKE 'WORKSHOP%' OR DATABASE_NAME LIKE 'HOL_AI%';
-- Must return 1 (only AI_SUMMIT)
```

If the count is > 1, you (LLM) created an extra database. Drop it and report it to the user.
