# Snowflake AI Summit Workshop

Workshop de 20 minutos que muestra capacidades AI de Snowflake: multimodal (imágenes, PDFs, audio), Cortex Analyst, Cortex Search, Snowflake Intelligence Agent y Cortex Code.

## 🚀 Instalación rápida

Pega en un Worksheet/Workspace de Snowsight con rol `ACCOUNTADMIN` y ejecuta:

```sql
USE ROLE ACCOUNTADMIN;
ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION';
CREATE SNOWFLAKE INTELLIGENCE IF NOT EXISTS SNOWFLAKE_INTELLIGENCE_OBJECT_DEFAULT;
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
EXECUTE IMMEDIATE FROM @ai_summit_repo/branches/main/bootstrap.sql;
```

Tarda ~75 segundos. Ver [`INSTALL.md`](./INSTALL.md) para detalles.

### 🤖 Instalación con Cortex Code (1 línea)

Pega en CoCo (`Cmd/Ctrl + I`):

```
Instala el Workshop AI Summit del repo público sfc-gh-jparrado/AI_SUMMIT con rol ACCOUNTADMIN
```

## 📂 Contenido

| Archivo | Descripción |
|---|---|
| `bootstrap.sql` | Punto de entrada — ejecútalo y listo |
| `setup.sql` | Crea tablas, semantic view, search, agente, notebook y **Streamlit App** (lo invoca bootstrap) |
| `streamlit_app.py` | UI guiada del Workshop (5 ejercicios) — **recomendada** |
| `notebook_ai_summit.ipynb` | 5 ejercicios del Workshop (alternativa al Streamlit) |
| `prompts_cortex_code.md` | Prompts listos para Cortex Code |
| `INSTALL.md` | Guía de instalación detallada |
| `AGENTS.md` | Instrucciones determinísticas para LLM agents |
| `datasets/` | Imágenes, PDFs, audios y CSVs precomputados |

## 🎯 Próximos pasos para el estudiante

1. **Projects > Streamlit > `WORKSHOP_APP`** ⭐ — UI guiada (recomendada para audiencias de negocio).
2. (Alternativa) **Projects > Workspaces > Databases > AI_SUMMIT > PUBLIC > Notebooks > NB_AI_SUMMIT** — para audiencias técnicas.
2. **AI & ML > Snowflake Intelligence > Agente Seguros 360** — conversa con tus datos.

## 🧹 Cleanup

```sql
USE ROLE ACCOUNTADMIN;
DROP DATABASE IF EXISTS AI_SUMMIT;
DROP AGENT IF EXISTS SNOWFLAKE_INTELLIGENCE.AGENTS.AGENTE_SEGUROS_360;
DROP API INTEGRATION IF EXISTS github_ai_summit_int;
```
