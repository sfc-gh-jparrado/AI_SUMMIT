# Guion de Prompts para Cortex Code (Workshop AI Summit)

> **Como usarlo:** Abre **Cortex Code** (icono de chispa abajo a la derecha en Snowsight) con rol `ACCOUNTADMIN`. Las reglas y rutas estan en `AGENTS.md` del repo: el LLM las sigue automaticamente. Por eso los prompts son cortos.

---

## Instalacion del Workshop - 4 prompts modulares (recomendado)

> **Por que modular:** cada prompt es corto, idempotente y tiene un objetivo unico. CoCo no se confunde, los errores se aislan, y los prompts 1 y 2 pueden correrse **en paralelo** una vez terminado el prompt 0.

### Prompt 0 - Foundation (DB, GIT, stages, tablas)

Tiempo aprox: ~30 segundos.

```
Necesito instalar el Workshop AI Summit en mi cuenta de Snowflake.

Repo publico: https://github.com/sfc-gh-jparrado/AI_SUMMIT

Por favor, usando el rol ACCOUNTADMIN:
1. Conecta el repo con una API integration y un Git repository
2. Ejecuta el archivo 00_base.sql del branch main
3. La unica base de datos que se debe crear se llama AI_SUMMIT (no inventes otros nombres)
```

### Prompt 1 - Streamlit + Notebook (las AI Functions)

Tiempo aprox: ~10 segundos. Requiere prompt 0 ya completado.

```
Sigamos con el Workshop AI Summit. Despliega la app guiada: con rol ACCOUNTADMIN, ejecuta el archivo 01_streamlit.sql del repo ai_summit_repo (branch main).
```

### Prompt 2 - Cortex Analyst + Cortex Search

Tiempo aprox: ~45 segundos. Requiere prompt 0 ya completado. Puede correrse en paralelo con prompt 1.

```
Sigamos con el Workshop AI Summit. Crea las herramientas de IA (Cortex Analyst y Cortex Search): con rol ACCOUNTADMIN, ejecuta el archivo 02_analyst_search.sql del repo ai_summit_repo (branch main).
```

### Prompt 3 - Snowflake Intelligence Agent

Tiempo aprox: ~5 segundos. Requiere prompts 0 y 2 completados.

```
Cerremos el Workshop AI Summit con el agente conversacional: con rol ACCOUNTADMIN, ejecuta el archivo 03_agent.sql del repo ai_summit_repo (branch main). Este agente combina Cortex Analyst, Cortex Search y graficos automaticos.
```

---

## Alternativa: instalacion en un solo paso

> Mas simple pero **mas lento** (~90s en serie) y, si falla en medio, mas dificil de diagnosticar.

```
Instala todo el Workshop AI Summit (one-shot). Sigue AGENTS.md.
```

---

## Prompts del Ejercicio "Cortex Code" (Tab del Streamlit)

Estos prompts los ejecuta el estudiante despues del setup, dentro del Streamlit (Tab "Cortex Code") o directamente en Cortex Code de Snowsight.

### Prompt - Vista de imagenes clasificadas

```
Crea una vista llamada V_IMAGENES_CLASIFICADAS que recorra todos los archivos del stage @IMAGENES y agregue una columna con la clasificacion del tipo de imagen entre las opciones: cedula, accidente vehicular, factura, logo corporativo, otro. Usa AI_CLASSIFY directamente sobre cada archivo (TO_FILE).
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
