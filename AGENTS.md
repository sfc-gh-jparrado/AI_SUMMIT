# AGENTS.md — Workshop AI Summit

> **This file is for LLM agents (Cortex Code, Claude Code, Cursor, etc.).**
> If a user asks to install, deploy, or set up the "AI Summit" workshop / "Workshop AI Summit" / "HOL AI Summit", follow these instructions **verbatim**. Do NOT improvise.

## CRITICAL — Database name policy (read this first)

**The ONLY database the user wants is `AI_SUMMIT`.** No other names. No translations.

Before doing anything else, run this exact pre-flight script:

```sql
USE ROLE ACCOUNTADMIN;

-- 0. Pre-flight: drop any database that an LLM may have invented from natural language
--    (variants like AI_SUMMIT_WORKSHOP, WORKSHOP_AI_SUMMIT, HOL_AI_SUMMIT, etc. are NOT wanted)
DROP DATABASE IF EXISTS AI_SUMMIT_WORKSHOP;
DROP DATABASE IF EXISTS WORKSHOP_AI_SUMMIT;
DROP DATABASE IF EXISTS HOL_AI_SUMMIT;
DROP DATABASE IF EXISTS AI_SUMMIT_HOL;
DROP DATABASE IF EXISTS WORKSHOP_AI;
DROP DATABASE IF EXISTS AISUMMIT;
DROP DATABASE IF EXISTS WORKSHOP;
```

**Rule:** if you (LLM) feel tempted to create a database with any name **other than `AI_SUMMIT`**, STOP. Use `AI_SUMMIT` and only `AI_SUMMIT`. The bootstrap script below creates it correctly.

## Authoritative install procedure

Execute this **complete** script as ONE unit (do not split, do not reorder, do not rename):

```sql
USE ROLE ACCOUNTADMIN;

-- Pre-flight cleanup (kill any wrong-name DB an LLM might have created)
DROP DATABASE IF EXISTS AI_SUMMIT_WORKSHOP;
DROP DATABASE IF EXISTS WORKSHOP_AI_SUMMIT;
DROP DATABASE IF EXISTS HOL_AI_SUMMIT;

-- Cross-region inference (required for Claude models)
ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION';

-- Snowflake Intelligence registry (required for the agent to appear in chat)
CREATE SNOWFLAKE INTELLIGENCE IF NOT EXISTS SNOWFLAKE_INTELLIGENCE_OBJECT_DEFAULT;

-- The ONE database for the Workshop
CREATE DATABASE IF NOT EXISTS AI_SUMMIT;
USE DATABASE AI_SUMMIT;
USE SCHEMA PUBLIC;

CREATE WAREHOUSE IF NOT EXISTS AI_SUMMIT_WH
  WAREHOUSE_SIZE = XSMALL
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = FALSE;
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
EXECUTE IMMEDIATE FROM @ai_summit_repo/branches/main/bootstrap.sql;
```

**Reference:** the actual `bootstrap.sql` at the repo root contains the same logic plus the call to `setup.sql`. Use either approach — both produce the SAME result.

## Hard-coded names (DO NOT modify)

| Object | Name |
|---|---|
| Database | `AI_SUMMIT` |
| Warehouse | `AI_SUMMIT_WH` |
| API integration | `github_ai_summit_int` |
| Git repo | `ai_summit_repo` |
| Agent | `SNOWFLAKE_INTELLIGENCE.AGENTS.AGENTE_SEGUROS_360` |
| Notebook | `NB_AI_SUMMIT` |
| Cortex Search | `DOCS_SEARCH` |
| Semantic View | `SV_SEGUROS` |

## Verification (run after install)

```sql
SHOW DATABASES LIKE 'AI_SUMMIT%';  -- expect ONLY AI_SUMMIT (no AI_SUMMIT_WORKSHOP)
SHOW AGENTS LIKE 'AGENTE_SEGUROS_360' IN SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS;
SHOW NOTEBOOKS LIKE 'NB_AI_SUMMIT' IN SCHEMA AI_SUMMIT.PUBLIC;
SELECT COUNT(*) FROM AI_SUMMIT.PUBLIC.POLIZAS;  -- expect 30
```

## Things NOT to do (cumulative)

- ❌ Do NOT create any database with a name OTHER than `AI_SUMMIT`. No `AI_SUMMIT_WORKSHOP`, no `WORKSHOP_AI_SUMMIT`, no `HOL_AI_SUMMIT`. If you (LLM) feel a different name fits better, **you are wrong** — use `AI_SUMMIT`.
- ❌ Do NOT translate "Workshop AI Summit" into a database identifier. The repo name `AI_SUMMIT` is the database name.
- ❌ Do NOT generate alternative SQL "from scratch". Always run the script above or `bootstrap.sql` from the repo.
- ❌ Do NOT change `WAREHOUSE_SIZE` from `XSMALL`.
- ❌ Do NOT skip `ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION'`.
- ❌ Do NOT create the agent in `AI_SUMMIT.PUBLIC` — must be in `SNOWFLAKE_INTELLIGENCE.AGENTS`.
- ❌ Do NOT execute `setup.sql` standalone — `bootstrap.sql` invokes it.

## Self-check before responding to user

After execution, verify only ONE workshop database exists:

```sql
SELECT COUNT(*) AS workshop_dbs FROM SNOWFLAKE.INFORMATION_SCHEMA.DATABASES
WHERE DATABASE_NAME LIKE 'AI_SUMMIT%' OR DATABASE_NAME LIKE 'WORKSHOP%' OR DATABASE_NAME LIKE 'HOL_AI%';
-- Must return 1 (only AI_SUMMIT)
```

If the count is > 1, you (LLM) created an extra database. Drop it and report it to the user.
