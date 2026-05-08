-- =====================================================================
-- Workshop AI SUMMIT - 03 SNOWFLAKE INTELLIGENCE AGENT - PASO 3 DE 4
-- =====================================================================
-- LLM/AGENTE: si el usuario menciona "agente", "agent", "snowflake
-- intelligence" o "paso 3", ejecuta SOLO este archivo. NO ejecutes
-- setup.sql ni los otros modulos. Requiere 00 + 02 ya completados.
-- =====================================================================
-- ORDEN DE EJECUCION: archivo 4 de 4. Requiere 00_base.sql Y 02_analyst_search.sql.
-- Crea: AGENTE_SEGUROS_360 en SNOWFLAKE_INTELLIGENCE.AGENTS, integra
--       Cortex Analyst (SV_SEGUROS) + Cortex Search (DOCS_SEARCH) + data_to_chart.
--       Lo registra en el Snowflake Intelligence Object para que aparezca en la UI.
-- =====================================================================
-- DURATION: ~5s
-- IDEMPOTENT: TRUE  (CREATE OR REPLACE + DROP IF EXISTS antes de ADD AGENT)
-- ROLE_REQUIRED: ACCOUNTADMIN (con SNOWFLAKE_INTELLIGENCE_ADMIN heredado, ver 00_base)
-- DEPENDS_ON:
--   - 00_base.sql (DB, schema, warehouse, SI Object, grants base)
--   - 02_analyst_search.sql (SV_SEGUROS y DOCS_SEARCH deben existir)
-- =====================================================================

USE ROLE ACCOUNTADMIN;
-- Activar todas las roles secundarias del usuario (SNOWFLAKE_INTELLIGENCE_ADMIN
-- viene heredado por ACCOUNTADMIN desde 00_base, pero esto es cinturon adicional).
USE SECONDARY ROLES ALL;
USE DATABASE AI_SUMMIT;
USE SCHEMA PUBLIC;
USE WAREHOUSE AI_SUMMIT_WH;

-- ---------------------------------------------------------------------
-- 1. Grants para SNOWFLAKE_INTELLIGENCE_ADMIN sobre los recursos del agente.
--    El rol que crea el agente necesita USAGE/SELECT sobre las herramientas
--    referenciadas (semantic view + cortex search). Sin esto, el agente
--    se crea pero falla al invocar las tools en runtime.
-- ---------------------------------------------------------------------
GRANT USAGE  ON DATABASE AI_SUMMIT                            TO ROLE SNOWFLAKE_INTELLIGENCE_ADMIN;
GRANT USAGE  ON SCHEMA   AI_SUMMIT.PUBLIC                     TO ROLE SNOWFLAKE_INTELLIGENCE_ADMIN;
GRANT SELECT ON ALL TABLES IN SCHEMA AI_SUMMIT.PUBLIC         TO ROLE SNOWFLAKE_INTELLIGENCE_ADMIN;
GRANT SELECT ON SEMANTIC VIEW AI_SUMMIT.PUBLIC.SV_SEGUROS     TO ROLE SNOWFLAKE_INTELLIGENCE_ADMIN;
GRANT USAGE  ON CORTEX SEARCH SERVICE AI_SUMMIT.PUBLIC.DOCS_SEARCH TO ROLE SNOWFLAKE_INTELLIGENCE_ADMIN;

-- ---------------------------------------------------------------------
-- 2. Crear / reemplazar el agente
-- ---------------------------------------------------------------------
CREATE OR REPLACE AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.AGENTE_SEGUROS_360
  WITH PROFILE='{"display_name": "Agente Seguros 360"}'
  COMMENT = 'Agente inteligente que analiza datos de pólizas, busca en contratos y genera gráficos'
  FROM SPECIFICATION $$
{
  "models": {"orchestration": "claude-4-sonnet"},
  "instructions": {
    "response": "Responde siempre en español, de forma clara y profesional. Cuando cites datos numéricos, indica la fuente. Usa gráficos cuando sea posible para visualizar tendencias.",
    "orchestration": "Para preguntas sobre ventas, pólizas, clientes, reclamaciones o métricas de negocio, usa la herramienta analizar_datos (Cortex Analyst). Para preguntas sobre contratos, cláusulas legales, transcripciones de llamadas o contenido de documentos, usa buscar_documentos (Cortex Search). Siempre que puedas responder visualmente con un gráfico, genera uno.",
    "system": "Eres un asistente inteligente de una empresa de seguros e inmobiliaria en Colombia. Tienes acceso a datos de pólizas vendidas, información de clientes, reclamaciones por siniestros, contratos de arrendamiento y transcripciones de llamadas de servicio al cliente."
  },
  "tools": [
    {
      "tool_spec": {
        "type": "cortex_analyst_text_to_sql",
        "name": "analizar_datos",
        "description": "Analiza datos estructurados de pólizas de seguros, clientes y reclamaciones. Usa esta herramienta para preguntas sobre ventas, ingresos por primas, rendimiento de vendedores, siniestros, métricas de negocio y segmentación de clientes."
      }
    },
    {
      "tool_spec": {
        "type": "cortex_search",
        "name": "buscar_documentos",
        "description": "Busca información en contratos de arrendamiento y transcripciones de llamadas de servicio al cliente. Usa esta herramienta para preguntas sobre cláusulas contractuales, términos legales, quejas de clientes, ofertas realizadas por teléfono y detalles de conversaciones."
      }
    },
    {
      "tool_spec": {
        "type": "data_to_chart",
        "name": "data_to_chart",
        "description": "Genera visualizaciones y gráficos a partir de datos. Usa siempre que puedas responder visualmente."
      }
    }
  ],
  "tool_resources": {
    "analizar_datos": {
      "semantic_view": "AI_SUMMIT.PUBLIC.SV_SEGUROS"
    },
    "buscar_documentos": {
      "name": "AI_SUMMIT.PUBLIC.DOCS_SEARCH",
      "max_results": 5,
      "id_column": "file_name",
      "title_column": "tipo_documento"
    }
  }
}
$$;

-- ---------------------------------------------------------------------
-- 3. Visibilidad: grants para que el agente sea visible/usable desde la UI
-- ---------------------------------------------------------------------
GRANT USAGE ON DATABASE SNOWFLAKE_INTELLIGENCE TO ROLE PUBLIC;
GRANT USAGE ON SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS TO ROLE PUBLIC;
GRANT USAGE ON AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.AGENTE_SEGUROS_360 TO ROLE PUBLIC;

-- ---------------------------------------------------------------------
-- 4. Registrar el agente en el Snowflake Intelligence Object (UI de chat).
--    El DROP previo es idempotente: si el agente no estaba registrado,
--    silenciamos el error con un bloque EXCEPTION.
-- ---------------------------------------------------------------------
EXECUTE IMMEDIATE $$
BEGIN
  ALTER SNOWFLAKE INTELLIGENCE SNOWFLAKE_INTELLIGENCE_OBJECT_DEFAULT
    DROP AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.AGENTE_SEGUROS_360;
EXCEPTION
  WHEN OTHER THEN
    RETURN 'agent not previously registered, skipping drop';
END;
$$;

ALTER SNOWFLAKE INTELLIGENCE SNOWFLAKE_INTELLIGENCE_OBJECT_DEFAULT
  ADD AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.AGENTE_SEGUROS_360;

GRANT USAGE ON SNOWFLAKE INTELLIGENCE SNOWFLAKE_INTELLIGENCE_OBJECT_DEFAULT TO ROLE PUBLIC;

-- ---------------------------------------------------------------------
-- Confirmacion
-- ---------------------------------------------------------------------
SELECT '03_agent.sql completado' AS status,
       'Agent: SNOWFLAKE_INTELLIGENCE.AGENTS.AGENTE_SEGUROS_360' AS agent,
       'Abre AI & ML > Snowflake Intelligence > Agente Seguros 360' AS donde_chatear,
       'Si no aparece, refresca la pagina de Snowsight' AS tip;
