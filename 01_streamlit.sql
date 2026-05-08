-- =====================================================================
-- Workshop AI SUMMIT - 01 STREAMLIT - PASO 1 DE 4
-- =====================================================================
-- LLM/AGENTE: si el usuario menciona "streamlit" o "paso 1",
-- ejecuta SOLO este archivo. NO ejecutes setup.sql ni los otros modulos.
-- Requiere 00_base.sql ya completado. Sigue las reglas en AGENTS.md.
-- =====================================================================
-- ORDEN DE EJECUCION: archivo 2 de 4. Requiere 00_base.sql ya ejecutado.
-- Crea: Streamlit App WORKSHOP_APP desde el repo Git. La app cubre los
--       5 ejercicios + Bonus de AI Functions (AI_COMPLETE, AI_EXTRACT,
--       AI_TRANSCRIBE, AI_SENTIMENT, AI_FILTER, AI_REDACT, AI_AGG, AI_CLASSIFY).
-- Las AI Functions se ejecutan en RUNTIME desde el Streamlit; aqui solo
-- se crea el contenedor de la app. Es independiente de Cortex Analyst /
-- Cortex Search / Agent (esos van en 02 y 03), por lo que el alumno puede
-- empezar a usar Tabs Imagenes/Documentos/Audio/Bonus mientras 02 y 03 corren.
-- =====================================================================
-- DURATION: ~10s
-- IDEMPOTENT: TRUE  (CREATE OR REPLACE)
-- ROLE_REQUIRED: ACCOUNTADMIN
-- DEPENDS_ON: 00_base.sql (DB, schema, warehouse, GIT repo)
-- =====================================================================

USE ROLE ACCOUNTADMIN;
USE DATABASE AI_SUMMIT;
USE SCHEMA PUBLIC;
USE WAREHOUSE AI_SUMMIT_WH;

-- Asegurar que el repo este al ultimo commit antes de crear los objetos
ALTER GIT REPOSITORY AI_SUMMIT.PUBLIC.AI_SUMMIT_REPO FETCH;

-- ---------------------------------------------------------------------
-- 1. Streamlit-in-Snowflake (UI principal del Workshop)
-- ---------------------------------------------------------------------
CREATE OR REPLACE STREAMLIT WORKSHOP_APP
  FROM '@AI_SUMMIT.PUBLIC.AI_SUMMIT_REPO/branches/main/'
  MAIN_FILE = 'streamlit_app.py'
  QUERY_WAREHOUSE = AI_SUMMIT_WH
  TITLE = 'Workshop AI Summit'
  COMMENT = 'UI guiada del Workshop AI Summit (bienvenida + 5 ejercicios + bonus AI Functions)';

GRANT USAGE ON STREAMLIT AI_SUMMIT.PUBLIC.WORKSHOP_APP TO ROLE PUBLIC;

-- ---------------------------------------------------------------------
-- Confirmacion
-- ---------------------------------------------------------------------
SELECT '01_streamlit.sql completado' AS status,
       'Streamlit listo: AI & ML > Streamlit Apps > WORKSHOP_APP' AS streamlit,
       'Tabs Imagenes/Documentos/Audio/Bonus ya funcionan. El agente requiere 02 + 03.' AS nota;
