"""Workshop AI Summit — Streamlit-in-Snowflake App.

Guía paso a paso de los 5 ejercicios del Workshop con UI amigable
para audiencias de negocio.
"""

import json

import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="Workshop AI Summit", page_icon="❄️", layout="wide")

session = get_active_session()


# --------------------------------------------------------------------- helpers
def run_sql(sql: str):
    """Run SQL and return pandas DataFrame."""
    return session.sql(sql).to_pandas()


def show_sql(sql: str, label: str = "SQL que vamos a ejecutar"):
    """Render a SQL block with a nice label."""
    with st.expander(f"🔍 {label}", expanded=False):
        st.code(sql, language="sql")


def render_json(value):
    """Render JSON-ish value nicely; fallback to string."""
    if value is None:
        st.write("_(sin resultado)_")
        return
    try:
        if isinstance(value, str):
            value = json.loads(value)
        st.json(value)
    except Exception:
        st.write(value)


# --------------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("### ❄️ Workshop AI Summit")
    st.markdown("**20 minutos · 5 ejercicios**")
    st.divider()
    st.markdown("**Contexto**")
    st.code(f"DB: AI_SUMMIT\nWH: AI_SUMMIT_WH", language="text")
    st.divider()
    st.markdown(
        "**Tip:** ejecuta los ejercicios en orden. "
        "Cada uno muestra el SQL y luego ejecuta al darle click."
    )
    st.divider()
    st.link_button(
        "🤖 Abrir Snowflake Intelligence", "https://ai.snowflake.com", use_container_width=True
    )


# --------------------------------------------------------------------- header
st.title("Workshop AI Summit — IA Multimodal con Snowflake")
st.markdown(
    "**Hoy vamos a ver cómo Snowflake procesa imágenes, documentos y audio "
    "con IA nativa**, y cómo cualquier persona puede crear agentes "
    "conversacionales con **Cortex Code**."
)

# --------------------------------------------------------------------- tabs
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "👋 Bienvenida",
        "🖼️ Ej. 1 · Imágenes",
        "📄 Ej. 2 · Documentos",
        "🎙️ Ej. 3 · Audio",
        "💬 Ej. 4 · Cortex Code",
        "🤖 Ej. 5 · Agente",
    ]
)

# =================================================================== Tab 0
with tab0:
    st.subheader("Datos con los que vamos a trabajar")
    st.markdown(
        "Una empresa de seguros e inmobiliaria en Colombia. "
        "Vamos a procesar **3 tipos de datos no estructurados** + **3 tablas de negocio**."
    )

    c1, c2, c3 = st.columns(3)
    try:
        c1.metric(
            "Imágenes",
            run_sql("SELECT COUNT(*) AS n FROM DIRECTORY(@AI_SUMMIT.PUBLIC.IMAGENES)").iloc[0][
                "N"
            ],
        )
        c2.metric(
            "Documentos PDF",
            run_sql("SELECT COUNT(*) AS n FROM DIRECTORY(@AI_SUMMIT.PUBLIC.DOCUMENTOS)").iloc[0][
                "N"
            ],
        )
        c3.metric(
            "Audios",
            run_sql("SELECT COUNT(*) AS n FROM DIRECTORY(@AI_SUMMIT.PUBLIC.AUDIO)").iloc[0]["N"],
        )
    except Exception as e:
        st.warning(f"No pude leer los stages: {e}")

    st.divider()

    st.markdown("#### 🖼️ Imágenes que vamos a analizar")
    try:
        imgs = run_sql(
            "SELECT RELATIVE_PATH, GET_PRESIGNED_URL(@AI_SUMMIT.PUBLIC.IMAGENES, RELATIVE_PATH, 3600) AS URL "
            "FROM DIRECTORY(@AI_SUMMIT.PUBLIC.IMAGENES) ORDER BY RELATIVE_PATH"
        )
        cols = st.columns(max(1, len(imgs)))
        for i, row in imgs.iterrows():
            with cols[i]:
                st.image(row["URL"], caption=row["RELATIVE_PATH"], use_container_width=True)
    except Exception as e:
        st.warning(f"Error mostrando imágenes: {e}")

    st.divider()

    st.markdown("#### 🎙️ Audios de llamadas reales")
    try:
        audios = run_sql(
            "SELECT RELATIVE_PATH, GET_PRESIGNED_URL(@AI_SUMMIT.PUBLIC.AUDIO, RELATIVE_PATH, 3600) AS URL "
            "FROM DIRECTORY(@AI_SUMMIT.PUBLIC.AUDIO) ORDER BY RELATIVE_PATH"
        )
        for _, row in audios.iterrows():
            st.write(f"**{row['RELATIVE_PATH']}**")
            st.audio(row["URL"])
    except Exception as e:
        st.warning(f"Error mostrando audios: {e}")

    st.divider()

    st.markdown("#### 📄 Contratos PDF")
    try:
        docs = run_sql(
            "SELECT RELATIVE_PATH, GET_PRESIGNED_URL(@AI_SUMMIT.PUBLIC.DOCUMENTOS, RELATIVE_PATH, 3600) AS URL "
            "FROM DIRECTORY(@AI_SUMMIT.PUBLIC.DOCUMENTOS) ORDER BY RELATIVE_PATH"
        )
        for _, row in docs.iterrows():
            st.markdown(f"- [{row['RELATIVE_PATH']}]({row['URL']})")
    except Exception as e:
        st.warning(f"Error mostrando PDFs: {e}")

    st.info(
        "👉 **Pasa a la siguiente pestaña para empezar el Ejercicio 1.** "
        "Vamos a hacer que Claude-4 *vea* las imágenes."
    )

# =================================================================== Tab 1
with tab1:
    st.subheader("Ejercicio 1 · Imágenes con IA Multimodal")
    st.markdown(
        "Vamos a usar `AI_COMPLETE` con un modelo multimodal (**Claude-4 Sonnet**) "
        "para analizar imágenes directamente desde un stage. Snowflake las **ve** como un humano."
    )

    st.markdown("#### 📸 Caso 1 — Análisis de un siniestro vehicular")
    try:
        url = run_sql(
            "SELECT GET_PRESIGNED_URL(@AI_SUMMIT.PUBLIC.IMAGENES, 'choque.png', 3600) AS U"
        ).iloc[0]["U"]
        st.image(url, caption="choque.png", width=400)
    except Exception:
        pass

    sql_choque = """SELECT AI_COMPLETE(
  'claude-4-sonnet',
  'Eres un perito de seguros. Describe el daño del vehiculo en esta imagen, indica severidad (leve/moderado/grave) y estima un rango de costo de reparacion en USD. Responde en español y en formato JSON con campos: descripcion, severidad, costo_estimado.',
  TO_FILE('@AI_SUMMIT.PUBLIC.IMAGENES', 'choque.png')
) AS analisis_siniestro;"""
    show_sql(sql_choque)

    if st.button("▶️ Analizar siniestro", key="btn_choque", type="primary"):
        with st.spinner("Claude-4 está analizando la imagen..."):
            try:
                df = run_sql(sql_choque)
                st.success("✅ Análisis completado")
                render_json(df.iloc[0]["ANALISIS_SINIESTRO"])
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()

    st.markdown("#### 🪪 Caso 2 — KYC: extracción de datos de cédula con `AI_EXTRACT`")
    try:
        url = run_sql(
            "SELECT GET_PRESIGNED_URL(@AI_SUMMIT.PUBLIC.IMAGENES, 'cedula.jpg', 3600) AS U"
        ).iloc[0]["U"]
        st.image(url, caption="cedula.jpg", width=400)
    except Exception:
        pass

    sql_cedula = """SELECT AI_EXTRACT(
  TO_FILE('@AI_SUMMIT.PUBLIC.IMAGENES', 'cedula.jpg'),
  ['nombres', 'apellidos', 'numero_cedula', 'fecha_expedicion', 'edad']
):response::VARIANT AS datos_cedula;"""
    show_sql(sql_cedula)

    if st.button("▶️ Extraer datos KYC", key="btn_cedula", type="primary"):
        with st.spinner("Extrayendo campos..."):
            try:
                df = run_sql(sql_cedula)
                st.success("✅ Extracción completada")
                render_json(df.iloc[0]["DATOS_CEDULA"])
            except Exception as e:
                st.error(f"Error: {e}")

    st.info(
        "💡 **Insight:** una sola función SQL reemplaza un pipeline de OCR + parsing + validación. "
        "Snowflake mantiene los datos donde ya viven, sin moverlos."
    )

# =================================================================== Tab 2
with tab2:
    st.subheader("Ejercicio 2 · Documentos a datos estructurados")
    st.markdown(
        "Snowflake procesa **PDF, DOCX, PPTX y más** sin pre-procesar. "
        "Convertimos contratos legales en datos consumibles por cualquier sistema."
    )

    st.markdown("#### 📋 Contratos ya parseados (creados por el setup)")
    try:
        df = run_sql(
            "SELECT file_name AS contrato, LEFT(content, 250) AS preview FROM AI_SUMMIT.PUBLIC.DOCS_PARSED"
        )
        st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error: {e}")

    st.divider()

    st.markdown("#### 🎯 Extraer campos clave con `AI_EXTRACT`")
    sql_extract = """SELECT
  file_name,
  AI_EXTRACT(
    content,
    ['arrendador', 'arrendatario', 'valor_canon_mensual', 'plazo_meses',
     'direccion_inmueble', 'fecha_inicio', 'numero_poliza_seguro', 'aseguradora']
  ) AS campos_extraidos
FROM AI_SUMMIT.PUBLIC.DOCS_PARSED;"""
    show_sql(sql_extract)

    if st.button("▶️ Extraer campos de contratos", key="btn_extract", type="primary"):
        with st.spinner("Extrayendo campos de los contratos..."):
            try:
                df = run_sql(sql_extract)
                for _, row in df.iterrows():
                    with st.expander(f"📄 {row['FILE_NAME']}", expanded=True):
                        render_json(row["CAMPOS_EXTRAIDOS"])
            except Exception as e:
                st.error(f"Error: {e}")

    st.info(
        "💡 **Insight:** los equipos legales y operaciones se ahorran horas. "
        "Cada campo extraído se puede unir directamente con tu tabla de pólizas."
    )

# =================================================================== Tab 3
with tab3:
    st.subheader("Ejercicio 3 · Audio con AI_TRANSCRIBE + AI_SENTIMENT + Coaching")
    st.markdown(
        "Tomamos llamadas reales, las **transcribimos**, medimos **sentimiento** "
        "y generamos **coaching** para el asesor. Imagina esto sobre 10.000 llamadas/noche."
    )

    try:
        audios = run_sql(
            "SELECT file_name, transcripcion, sentimiento "
            "FROM AI_SUMMIT.PUBLIC.TRANSCRIPCIONES ORDER BY file_name"
        )
        urls = run_sql(
            "SELECT RELATIVE_PATH AS file_name, GET_PRESIGNED_URL(@AI_SUMMIT.PUBLIC.AUDIO, RELATIVE_PATH, 3600) AS URL "
            "FROM DIRECTORY(@AI_SUMMIT.PUBLIC.AUDIO)"
        )
        url_map = dict(zip(urls["FILE_NAME"], urls["URL"]))

        for _, row in audios.iterrows():
            sent = (row["SENTIMIENTO"] or "").lower()
            badge = {"positive": "🟢", "negative": "🔴", "mixed": "🟡", "neutral": "⚪"}.get(
                sent, "⚪"
            )
            st.markdown(f"#### {badge} `{row['FILE_NAME']}` — sentimiento: **{sent}**")
            if row["FILE_NAME"] in url_map:
                st.audio(url_map[row["FILE_NAME"]])
            with st.expander("Ver transcripción"):
                st.write(row["TRANSCRIPCION"])
            st.markdown("")
    except Exception as e:
        st.error(f"Error: {e}")

    st.divider()

    st.markdown("#### 🎓 Generar coaching para el asesor (JSON formateado)")
    sql_coach = """SELECT
  file_name,
  TRY_PARSE_JSON(
    AI_COMPLETE(
      'claude-4-sonnet',
      CONCAT(
        'Eres un coach experto en servicio al cliente. Analiza esta transcripción y genera recomendaciones para el asesor en formato JSON con: ',
        '{"puntos_dolor": [...], "fortalezas_asesor": [...], "areas_mejora": [...], "recomendacion_inmediata": "...", "script_sugerido": "frase exacta a usar en la próxima interacción"}. ',
        'Responde SOLO el JSON válido, sin markdown ni backticks, en español. Transcripción: ', transcripcion
      )
    )
  ) AS recomendaciones
FROM AI_SUMMIT.PUBLIC.TRANSCRIPCIONES;"""
    show_sql(sql_coach)

    if st.button("▶️ Generar coaching", key="btn_coach", type="primary"):
        with st.spinner("Generando recomendaciones..."):
            try:
                df = run_sql(sql_coach)
                for _, row in df.iterrows():
                    with st.expander(f"🎓 Coaching para {row['FILE_NAME']}", expanded=True):
                        render_json(row["RECOMENDACIONES"])
            except Exception as e:
                st.error(f"Error: {e}")

    st.info(
        "💡 **Insight:** combinamos 3 funciones AI en SQL plano. "
        "Sin notebooks externos, sin mover audio, sin pipelines."
    )

# =================================================================== Tab 4
with tab4:
    st.subheader("Ejercicio 4 · Cortex Code — construyamos en lenguaje natural")
    st.markdown(
        "Sal de esta app y abre **Cortex Code** en Snowsight (`Cmd/Ctrl + I` o ícono de chispa). "
        "Asegúrate de estar en `AI_SUMMIT.PUBLIC` con warehouse `AI_SUMMIT_WH`. "
        "Pega cada prompt y observa cómo Cortex Code genera el código."
    )

    prompts = [
        (
            "Vista que clasifica imágenes",
            "Crea una vista llamada V_IMAGENES_CLASIFICADAS que recorra todos los archivos "
            "del stage IMAGENES y agregue una columna con la clasificación del tipo de imagen "
            "(cédula, accidente vehicular, factura, otro) usando AI_CLASSIFY sobre AI_COMPLETE multimodal.",
        ),
        (
            "Vista 360 unificada",
            "Crea una vista llamada V_HOL_360 que combine las filas de DOCS_PARSED y "
            "TRANSCRIPCIONES en un solo dataset con columnas: tipo_fuente, archivo, contenido, sentimiento.",
        ),
        (
            "Conversa con tus datos",
            "Genera un SELECT que invoque a AI_COMPLETE preguntándole: ¿cuánto es el canon mensual "
            "del contrato número 2 y cuál fue el sentimiento de la última llamada?",
        ),
        (
            "App Streamlit dashboard",
            "Crea una app Streamlit in Snowflake llamada DASHBOARD_HOL que muestre el total de "
            "imágenes por tipo, el sentimiento de las llamadas en gráfico de barras, y un campo "
            "de chat conectado al agente.",
        ),
    ]

    for i, (title, prompt) in enumerate(prompts, 1):
        st.markdown(f"##### Prompt {i} — {title}")
        st.code(prompt, language="text")
        st.markdown("")

    st.info(
        "💡 **Insight:** una persona de negocio puede construir pipelines de IA productivos "
        "**sin esperar un sprint de desarrollo**. Esto cambia las reglas."
    )

# =================================================================== Tab 5
with tab5:
    st.subheader("Ejercicio 5 · Cortex Analyst + Search + Agente")
    st.markdown(
        "Cerramos con el **Snowflake Intelligence Agent** que combina texto-a-SQL "
        "(Cortex Analyst), búsqueda semántica (Cortex Search) y gráficos."
    )

    st.markdown("#### 📊 Cortex Analyst — preguntas en español sobre datos estructurados")
    sql_region = """SELECT region, SUM(prima_mensual) AS total_primas, COUNT(*) AS num_polizas
FROM AI_SUMMIT.PUBLIC.POLIZAS
WHERE estado = 'Activa'
GROUP BY region
ORDER BY total_primas DESC;"""
    show_sql(sql_region, "Verified Query: ventas por región")

    if st.button("▶️ Ejecutar query del Cortex Analyst", key="btn_region"):
        try:
            df = run_sql(sql_region)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.bar_chart(df.set_index("REGION")["TOTAL_PRIMAS"])
        except Exception as e:
            st.error(f"Error: {e}")

    st.divider()

    st.markdown("#### 🔎 Cortex Search — búsqueda semántica en contratos y llamadas")
    query = st.text_input("Tu búsqueda:", value="cliente molesto sin servicio")
    if st.button("▶️ Buscar", key="btn_search"):
        try:
            sql = f"""SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
  'AI_SUMMIT.PUBLIC.DOCS_SEARCH',
  '{{"query": "{query}", "columns": ["contenido","file_name","tipo_documento"], "limit": 3}}'
) AS R"""
            res = run_sql(sql).iloc[0]["R"]
            data = json.loads(res) if isinstance(res, str) else res
            for hit in data.get("results", []):
                with st.expander(
                    f"📌 {hit.get('file_name', '?')} ({hit.get('tipo_documento', '?')})"
                ):
                    st.write(hit.get("contenido", ""))
        except Exception as e:
            st.error(f"Error: {e}")

    st.divider()

    st.markdown("#### 🤖 Snowflake Intelligence Agent")
    st.markdown(
        "El agente `AGENTE_SEGUROS_360` ya está creado y combina los 3 tools: "
        "Cortex Analyst, Cortex Search y data_to_chart."
    )
    st.link_button(
        "🚀 Abrir el agente en Snowflake Intelligence",
        "https://ai.snowflake.com",
        type="primary",
        use_container_width=True,
    )

    st.success(
        "🎉 **¡Felicitaciones!** En 20 minutos pasaste de archivos crudos "
        "(imágenes, PDFs, audio) a un agente conversacional productivo. "
        "Todo dentro de Snowflake, sin mover datos."
    )
