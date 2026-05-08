-- =====================================================================
-- Workshop AI SUMMIT - SETUP TODO-EN-UNO (orquestador)
-- =====================================================================
-- Ejecuta los 4 modulos en orden: 00 -> 01 -> 02 -> 03.
-- Para CoCo / agentes LLM con tiempos limitados, usar los archivos
-- modulares por separado es mas rapido y menos propenso a errores:
--
--   00_base.sql              - DB, GIT, stages, tablas         (~30s)
--   01_streamlit.sql         - Notebook + Streamlit            (~10s)
--   02_analyst_search.sql    - Cortex Analyst + Cortex Search  (~45s)
--   03_agent.sql             - Snowflake Intelligence Agent    (~5s)
--
-- 01 y 02 son INDEPENDIENTES entre si: pueden correrse en paralelo.
-- 03 depende de 02.
--
-- Este archivo es para usuarios que prefieren un solo paste.
-- =====================================================================
-- DURATION: ~90s
-- IDEMPOTENT: TRUE
-- ROLE_REQUIRED: ACCOUNTADMIN
-- =====================================================================
-- INSTRUCCIONES PARA AGENTES LLM (Cortex Code, etc.):
--   - PREFIERE ejecutar los 4 archivos por separado (mas rapido, mas confiable).
--   - NO envuelvas estos archivos en otro EXECUTE IMMEDIATE.
--   - NO modifiques los nombres de objetos.
-- =====================================================================
-- CLEANUP opcional (descomenta solo si necesitas reinstalar desde cero):
-- DROP DATABASE IF EXISTS AI_SUMMIT;
-- DROP AGENT IF EXISTS SNOWFLAKE_INTELLIGENCE.AGENTS.AGENTE_SEGUROS_360;
-- DROP API INTEGRATION IF EXISTS github_ai_summit_int;
-- =====================================================================

USE ROLE ACCOUNTADMIN;

-- ---------------------------------------------------------------------
-- BOOTSTRAP del GIT repository (necesario antes de poder hacer
-- EXECUTE IMMEDIATE FROM @repo). 00_base.sql vuelve a crearlo (idempotente).
-- ---------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS AI_SUMMIT;
USE DATABASE AI_SUMMIT;
CREATE SCHEMA IF NOT EXISTS PUBLIC;
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

-- ---------------------------------------------------------------------
-- Ejecutar los 4 modulos en orden
-- ---------------------------------------------------------------------
EXECUTE IMMEDIATE FROM @AI_SUMMIT.PUBLIC.AI_SUMMIT_REPO/branches/main/00_base.sql;
EXECUTE IMMEDIATE FROM @AI_SUMMIT.PUBLIC.AI_SUMMIT_REPO/branches/main/01_streamlit.sql;
EXECUTE IMMEDIATE FROM @AI_SUMMIT.PUBLIC.AI_SUMMIT_REPO/branches/main/02_analyst_search.sql;
EXECUTE IMMEDIATE FROM @AI_SUMMIT.PUBLIC.AI_SUMMIT_REPO/branches/main/03_agent.sql;

-- ---------------------------------------------------------------------
-- Resumen final
-- ---------------------------------------------------------------------
SELECT 'Setup completo (4 modulos ejecutados).' AS status,
       'Streamlit App: AI & ML > Streamlit Apps > WORKSHOP_APP' AS streamlit,
       'Cortex Analyst: AI_SUMMIT.PUBLIC.SV_SEGUROS' AS analyst,
       'Cortex Search: AI_SUMMIT.PUBLIC.DOCS_SEARCH' AS search,
       'Agent: AI & ML > Snowflake Intelligence > Agente Seguros 360' AS agent,
       'Si Snowflake Intelligence no aparece, refresca la pagina de Snowsight' AS tip;
