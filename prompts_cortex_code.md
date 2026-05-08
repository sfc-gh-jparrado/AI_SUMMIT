# Guion de Prompts para Cortex Code (Workshop AI Summit)

> **Como usarlo:** Abre **Cortex Code** en Snowsight haciendo clic en el icono de la chispa en la esquina inferior derecha. Asegurate de estar con rol `ACCOUNTADMIN` en el contexto `AI_SUMMIT.PUBLIC` con warehouse `AI_SUMMIT_WH`. Pega cada prompt y deja que Cortex Code genere y ejecute el SQL.

---

## Instalacion del Workshop - 4 prompts modulares (recomendado)

> **Por que modular:** cada prompt es corto, idempotente y tiene un objetivo unico. CoCo no se confunde, los errores se aislan, y los prompts 1 y 2 pueden correrse **en paralelo** una vez terminado el prompt 0.

### Prompt 0 - Foundation (DB, GIT, stages, tablas)

Tiempo aprox: ~30 segundos.

```
Conecta el repo publico https://github.com/sfc-gh-jparrado/AI_SUMMIT.git con una API integration y ejecuta SOLO el archivo 00_base.sql desde el repo, usando rol ACCOUNTADMIN. La unica base de datos permitida es AI_SUMMIT (no AI_SUMMIT_WORKSHOP, no WORKSHOP_AI_SUMMIT, no HOL_AI_SUMMIT). Antes de cualquier paso ejecuta DROP DATABASE IF EXISTS AI_SUMMIT_WORKSHOP, WORKSHOP_AI_SUMMIT, HOL_AI_SUMMIT. NO ejecutes setup.sql ni los otros archivos. Confirma al final que existen la base AI_SUMMIT, las tablas POLIZAS, CLIENTES, RECLAMACIONES, DOCS_PARSED, TRANSCRIPCIONES y los stages IMAGENES, DOCUMENTOS, AUDIO con archivos cargados.
```

### Prompt 1 - Streamlit + Notebook (las AI Functions)

Tiempo aprox: ~10 segundos. Requiere prompt 0 ya completado.

```
En AI_SUMMIT.PUBLIC con rol ACCOUNTADMIN ejecuta SOLO el archivo 01_streamlit.sql desde el repo Git ai_summit_repo (branch main). Esto crea el Notebook NB_AI_SUMMIT y la app Streamlit WORKSHOP_APP. Confirma al final que ambos existen y que la Streamlit es accesible en AI & ML > Streamlit Apps.
```

### Prompt 2 - Cortex Analyst + Cortex Search

Tiempo aprox: ~45 segundos. Requiere prompt 0 ya completado. Puede correrse en paralelo con prompt 1.

```
En AI_SUMMIT.PUBLIC con rol ACCOUNTADMIN ejecuta SOLO el archivo 02_analyst_search.sql desde el repo Git ai_summit_repo (branch main). Esto crea la tabla BASE_CONOCIMIENTO, el Cortex Search Service DOCS_SEARCH (con embedding snowflake-arctic-embed-l-v2.0) y la Semantic View SV_SEGUROS para Cortex Analyst con dimensiones, metricas y verified queries. Confirma al final que SV_SEGUROS y DOCS_SEARCH existen.
```

### Prompt 3 - Snowflake Intelligence Agent

Tiempo aprox: ~5 segundos. Requiere prompts 0 y 2 completados.

```
En AI_SUMMIT.PUBLIC con rol ACCOUNTADMIN ejecuta SOLO el archivo 03_agent.sql desde el repo Git ai_summit_repo (branch main). Esto crea el agente AGENTE_SEGUROS_360 en SNOWFLAKE_INTELLIGENCE.AGENTS integrando los 3 tools (Cortex Analyst sobre SV_SEGUROS, Cortex Search sobre DOCS_SEARCH, data_to_chart) y lo registra en el Snowflake Intelligence Object para que aparezca en la UI. Confirma al final que el agente existe y esta listado en SHOW AGENTS IN SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS.
```

---

## Alternativa: instalacion en un solo paso

> Mas simple pero **mas lento** (~90s en serie) y, si falla en medio, mas dificil de diagnosticar.

```
Instala el Workshop AI Summit del repo publico sfc-gh-jparrado/AI_SUMMIT con rol ACCOUNTADMIN. La UNICA base de datos permitida es AI_SUMMIT (no AI_SUMMIT_WORKSHOP, no WORKSHOP_AI_SUMMIT, no HOL_AI_SUMMIT). Antes de cualquier paso ejecuta DROP DATABASE IF EXISTS AI_SUMMIT_WORKSHOP, WORKSHOP_AI_SUMMIT, HOL_AI_SUMMIT. Luego ejecuta setup.sql del repo tal cual sin modificar nombres ni envolverlo en otro EXECUTE IMMEDIATE.
```

---

## Prompts del Ejercicio "Cortex Code" (Tab del Streamlit)

Estos prompts los ejecuta el estudiante despues del setup, dentro del Streamlit (Tab "Cortex Code") o directamente en Cortex Code de Snowsight.

### Prompt - Vista de imagenes clasificadas

```
Crea una vista llamada V_IMAGENES_CLASIFICADAS que recorra todos los archivos del stage @IMAGENES y agregue una columna con la clasificacion del tipo de imagen entre las opciones: cedula, accidente vehicular, factura, logo corporativo, otro. Usa AI_CLASSIFY sobre el resultado de AI_COMPLETE con un modelo multimodal.
```

### Prompt - Vista 360 multimodal

```
Crea una vista V_HOL_360 que unifique las filas de DOCS_PARSED y TRANSCRIPCIONES con columnas: tipo_fuente (documento o audio), archivo, contenido, sentimiento (NULL para documentos).
```

### Prompt - Conversa con tus datos

```
Genera un SELECT que invoque a AI_COMPLETE preguntando: cuanto es el canon mensual del contrato numero 2 y cual fue el sentimiento de la ultima llamada?
```

### Prompt - Streamlit dashboard

```
Crea una app Streamlit in Snowflake llamada DASHBOARD_HOL que muestre el total de imagenes por tipo, el sentimiento de las llamadas en grafico de barras, y un campo de chat conectado al agente.
```

---

## Bonus - Pruebas rapidas adicionales

- "Crea un dynamic table que mantenga DOCS_PARSED actualizada cada vez que se agregue un archivo nuevo al stage DOCUMENTOS."
- "Genera un task que ejecute AI_TRANSCRIBE diariamente sobre los nuevos archivos del stage AUDIO."
- "Hazme un row access policy para que solo el rol HR_ROLE pueda ver el contenido de los contratos."

---

## Mensaje para el asistente del Workshop

> Cortex Code te permite construir pipelines de IA, agentes y apps escribiendo en lenguaje natural. **No necesitas saber SQL avanzado**, no necesitas mover datos a otra plataforma, y todo queda gobernado por Snowflake. Esto es lo que diferencia a Snowflake de Databricks, Fabric, BigQuery o Redshift: **una sola plataforma, una experiencia conversacional, resultados productivos en minutos**.
