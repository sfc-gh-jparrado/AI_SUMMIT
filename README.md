# Snowflake AI Summit Workshop

Workshop de 20 minutos que muestra capacidades AI de Snowflake: multimodal (imagenes, PDFs, audio), Cortex Analyst, Cortex Search, Snowflake Intelligence Agent y Cortex Code.

## Instalacion - 2 caminos

### Camino A (recomendado): 4 prompts modulares en Cortex Code

Mas rapido, menos propenso a errores, y los prompts 1 y 2 corren en paralelo.

| Paso | Archivo | Tiempo | Que hace |
|---|---|---|---|
| **0** | `00_base.sql` | ~30s | DB, GIT, stages, archivos, tablas, prereqs |
| **1** | `01_streamlit.sql` | ~10s | Streamlit App |
| **2** | `02_analyst_search.sql` | ~45s | Semantic View + Cortex Search Service |
| **3** | `03_agent.sql` | ~5s | Snowflake Intelligence Agent |

Pasos 1 y 2 son independientes y pueden correrse en paralelo. Paso 3 depende de 2.

Ver [`prompts_cortex_code.md`](./prompts_cortex_code.md) para los prompts listos para pegar en Cortex Code.

### Camino B (one-shot): pega y ejecuta `setup.sql`

```sql
USE ROLE ACCOUNTADMIN;
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
EXECUTE IMMEDIATE FROM @ai_summit_repo/branches/main/setup.sql;
```

Tarda ~90 segundos en serie.

## Contenido

| Archivo | Descripcion |
|---|---|
| `00_base.sql` | Foundation: DB, GIT, stages, datos, tablas |
| `01_streamlit.sql` | Streamlit App |
| `02_analyst_search.sql` | Semantic View + Cortex Search Service |
| `03_agent.sql` | Snowflake Intelligence Agent |
| `setup.sql` | Orquestador one-shot (corre los 4 modulos en orden) |
| `streamlit_app.py` | UI guiada del Workshop (bienvenida + 5 ejercicios + bonus) |
| `prompts_cortex_code.md` | Prompts listos para Cortex Code |
| `INSTALL.md` | Guia de instalacion detallada |
| `AGENTS.md` | Instrucciones deterministicas para LLM agents |
| `datasets/` | Imagenes, PDFs, audios y CSVs precomputados |

## Proximos pasos para el estudiante

1. **Projects > Streamlit > `WORKSHOP_APP`** - UI guiada del Workshop
2. **AI & ML > Snowflake Intelligence > Agente Seguros 360** - conversa con tus datos

## Cleanup

```sql
USE ROLE ACCOUNTADMIN;
DROP DATABASE IF EXISTS AI_SUMMIT;
DROP AGENT IF EXISTS SNOWFLAKE_INTELLIGENCE.AGENTS.AGENTE_SEGUROS_360;
DROP API INTEGRATION IF EXISTS github_ai_summit_int;
```
