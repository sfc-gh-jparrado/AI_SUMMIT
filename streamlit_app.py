"""Workshop AI Summit - Streamlit-in-Snowflake App.

UI guiada de los 5 ejercicios del Workshop. Tema claro (Snowflake)
configurado en .streamlit/config.toml.
"""

import json

import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(
    page_title="Workshop AI Summit",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

session = get_active_session()


# =========================================================== helpers
def run_sql(sql: str):
    """Run SQL and return pandas DataFrame."""
    return session.sql(sql).to_pandas()


def editable_sql(key: str, default_sql: str, height: int = 200) -> str:
    """Render an editable SQL block with a reset-to-original button.

    The user can edit the SQL freely; if anything breaks, click "Restaurar"
    and the text area returns to the original query.
    """
    state_key = f"sql_{key}"
    reset_flag = f"reset_{key}_flag"

    # Apply pending reset BEFORE the widget is created
    if st.session_state.get(reset_flag):
        st.session_state[state_key] = default_sql
        st.session_state[reset_flag] = False

    if state_key not in st.session_state:
        st.session_state[state_key] = default_sql

    def _request_reset():
        st.session_state[reset_flag] = True

    cols = st.columns([6, 1])
    with cols[0]:
        st.caption(":blue[SQL editable] - modificalo libremente. Si rompes algo, usa Restaurar.")
    with cols[1]:
        st.button(
            "Restaurar", key=f"reset_{key}", on_click=_request_reset, use_container_width=True
        )

    edited = st.text_area(
        "SQL editable",
        key=state_key,
        height=height,
        label_visibility="collapsed",
    )
    return edited


def _strip_md_fences(text: str) -> str:
    """Strip markdown code fences (```json ... ```) commonly returned by LLMs."""
    s = text.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else s[3:]
    if s.endswith("```"):
        s = s[: -3]
    return s.strip()


def render_json(value):
    """Render JSON nicely; tolerate ```json fences and fallback to str."""
    if value is None:
        st.write("_(sin resultado)_")
        return
    try:
        if isinstance(value, str):
            value = json.loads(_strip_md_fences(value))
        st.json(value)
    except Exception:
        st.write(value)


def safe_run(sql: str, label: str = "Ejecutando..."):
    """Run SQL with spinner and friendly error message. Returns DataFrame or None."""
    try:
        with st.spinner(label):
            return run_sql(sql)
    except Exception as e:
        st.error(
            f"Error al ejecutar el SQL.\n\n```\n{e}\n```\n\n"
            "**Tip:** usa el boton :blue[Restaurar] para volver al SQL original."
        )
        return None


# =========================================================== hero
with st.container(border=True):
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown("### :blue[**Workshop AI Summit**] - IA Multimodal con Snowflake")
        st.caption(
            "20 minutos · 5 ejercicios · imagenes, documentos, audio + Cortex Code "
            "+ Snowflake Intelligence Agent"
        )
    with c2:
        st.markdown("**:gray[Contexto]**")
        st.code("DB: AI_SUMMIT\nWH: AI_SUMMIT_WH", language="text")

st.write("")  # spacer

# =========================================================== tabs
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Bienvenida",
        "Ej. 1 - Imagenes",
        "Ej. 2 - Documentos",
        "Ej. 3 - Audio",
        "Ej. 4 - Cortex Code",
        "Ej. 5 - Agente",
    ]
)

# =================================================================== Tab 0
with tab0:
    st.subheader("Bienvenido al Workshop")
    st.markdown(
        "En **20 minutos** vas a ver como Snowflake convierte datos **no estructurados** "
        "(imagenes, documentos, audio) en informacion accionable, **todo en SQL**, "
        "y al final lo vas a conversar con un **agente**."
    )

    st.write("")
    c1, c2, c3 = st.columns(3)
    try:
        c1.metric(
            "Imagenes",
            int(
                run_sql(
                    "SELECT COUNT(*) AS n FROM DIRECTORY(@AI_SUMMIT.PUBLIC.IMAGENES)"
                ).iloc[0]["N"]
            ),
        )
        c2.metric(
            "Documentos PDF",
            int(
                run_sql(
                    "SELECT COUNT(*) AS n FROM DIRECTORY(@AI_SUMMIT.PUBLIC.DOCUMENTOS)"
                ).iloc[0]["N"]
            ),
        )
        c3.metric(
            "Audios",
            int(
                run_sql(
                    "SELECT COUNT(*) AS n FROM DIRECTORY(@AI_SUMMIT.PUBLIC.AUDIO)"
                ).iloc[0]["N"]
            ),
        )
    except Exception as e:
        st.warning(f"No pude leer los stages: {e}")

    st.divider()
    st.markdown("#### El paso a paso")

    pasos = [
        (
            "1. Imagenes con IA multimodal",
            "Le pasamos a Claude-4 una foto de un siniestro y una cedula. "
            "En una sola consulta SQL obtenemos el peritaje y los datos para verificar la identidad del cliente.",
        ),
        (
            "2. Documentos a datos estructurados",
            "Tomamos contratos en PDF, los parseamos y con `AI_EXTRACT` "
            "sacamos arrendador, canon, plazo y poliza listos para tu data warehouse.",
        ),
        (
            "3. Audio: transcripcion + sentimiento + coaching",
            "Convertimos llamadas reales a texto, medimos el sentimiento del cliente "
            "y generamos coaching automatico para el asesor.",
        ),
        (
            "4. Cortex Code",
            "Le pides en lenguaje natural lo que necesitas (vistas, queries, hasta "
            "una app Streamlit) y Cortex Code escribe el codigo por ti.",
        ),
        (
            "5. Snowflake Intelligence Agent",
            "Cerramos con un agente que combina texto-a-SQL, busqueda semantica y "
            "graficos: hablale a tus datos en espanol.",
        ),
    ]

    for titulo, desc in pasos:
        with st.container(border=True):
            st.markdown(f"**:blue[{titulo}]**")
            st.markdown(desc)

    st.info(
        "Avanza a la pestana **Ej. 1 - Imagenes** para empezar. Cada query es "
        "editable: si rompes algo, usa el boton **Restaurar**."
    )

# =================================================================== Tab 1
with tab1:
    st.subheader("Ejercicio 1 - Imagenes con IA Multimodal")
    st.markdown(
        "Usamos `AI_COMPLETE` con **Claude-4 Sonnet** (multimodal) para analizar imagenes "
        "directamente desde un stage. Snowflake las **ve** como un humano."
    )

    st.markdown("##### Caso 1 - Analisis de un siniestro vehicular")
    try:
        url = run_sql(
            "SELECT GET_PRESIGNED_URL(@AI_SUMMIT.PUBLIC.IMAGENES, 'choque.png', 3600) AS U"
        ).iloc[0]["U"]
        with st.container(border=True):
            st.image(url, caption="choque.png", width=400)
    except Exception:
        pass

    sql_choque_default = """SELECT TRY_PARSE_JSON(
  REGEXP_REPLACE(
    AI_COMPLETE(
      'claude-4-sonnet',
      'Eres un perito de seguros. Describe el dano del vehiculo en esta imagen, indica severidad (leve/moderado/grave) y estima un rango de costo de reparacion en USD. Responde SOLO con un objeto JSON valido, sin markdown ni backticks ni texto adicional, en espanol, con los campos: descripcion, severidad, costo_estimado.',
      TO_FILE('@AI_SUMMIT.PUBLIC.IMAGENES', 'choque.png')
    ),
    '```(json)?', ''
  )
) AS analisis_siniestro;"""
    sql_choque = editable_sql("choque", sql_choque_default, height=200)

    if st.button("Analizar siniestro", key="btn_choque", type="primary"):
        df = safe_run(sql_choque, "Claude-4 esta analizando la imagen...")
        if df is not None:
            st.success("Analisis completado")
            render_json(df.iloc[0]["ANALISIS_SINIESTRO"])

    st.divider()
    st.markdown("##### Caso 2 - Verificacion de identidad: extraccion de datos de cedula con AI_EXTRACT")
    try:
        url = run_sql(
            "SELECT GET_PRESIGNED_URL(@AI_SUMMIT.PUBLIC.IMAGENES, 'cedula.jpg', 3600) AS U"
        ).iloc[0]["U"]
        with st.container(border=True):
            st.image(url, caption="cedula.jpg", width=400)
    except Exception:
        pass

    sql_cedula_default = """SELECT AI_EXTRACT(
  TO_FILE('@AI_SUMMIT.PUBLIC.IMAGENES', 'cedula.jpg'),
  ['nombres', 'apellidos', 'numero_cedula', 'fecha_expedicion', 'edad']
):response::VARIANT AS datos_cedula;"""
    sql_cedula = editable_sql("cedula", sql_cedula_default, height=140)

    if st.button("Extraer datos de identidad", key="btn_cedula", type="primary"):
        df = safe_run(sql_cedula, "Extrayendo campos...")
        if df is not None:
            st.success("Extraccion completada")
            render_json(df.iloc[0]["DATOS_CEDULA"])

    st.info(
        "**Insight:** una sola funcion SQL reemplaza un pipeline de OCR + parsing + validacion."
    )

# =================================================================== Tab 2
with tab2:
    st.subheader("Ejercicio 2 - Documentos a datos estructurados")
    st.markdown(
        "Snowflake procesa **PDF, DOCX, PPTX y mas** sin pre-procesar. "
        "Convertimos contratos legales en datos consumibles."
    )

    st.markdown("##### Contratos ya parseados (creados por el setup)")
    try:
        df = run_sql(
            "SELECT file_name AS contrato, LEFT(content, 250) AS preview "
            "FROM AI_SUMMIT.PUBLIC.DOCS_PARSED"
        )
        st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error: {e}")

    st.markdown("###### Descargar los contratos originales (PDF)")
    try:
        docs = run_sql(
            "SELECT RELATIVE_PATH, GET_PRESIGNED_URL(@AI_SUMMIT.PUBLIC.DOCUMENTOS, "
            "RELATIVE_PATH, 3600) AS URL FROM DIRECTORY(@AI_SUMMIT.PUBLIC.DOCUMENTOS) "
            "ORDER BY RELATIVE_PATH"
        )
        cols = st.columns(max(1, len(docs)))
        for i, row in docs.iterrows():
            with cols[i]:
                st.link_button(
                    f"Descargar {row['RELATIVE_PATH']}",
                    row["URL"],
                    use_container_width=True,
                )
    except Exception as e:
        st.warning(f"No se pudieron generar los enlaces: {e}")

    st.divider()
    st.markdown("##### Extraer campos clave con AI_EXTRACT")
    sql_extract_default = """SELECT
  file_name,
  AI_EXTRACT(
    content,
    ['arrendador', 'arrendatario', 'valor_canon_mensual', 'plazo_meses',
     'direccion_inmueble', 'fecha_inicio', 'numero_poliza_seguro', 'aseguradora']
  ) AS campos_extraidos
FROM AI_SUMMIT.PUBLIC.DOCS_PARSED;"""
    sql_extract = editable_sql("extract_docs", sql_extract_default, height=200)

    if st.button("Extraer campos de contratos", key="btn_extract", type="primary"):
        df = safe_run(sql_extract, "Extrayendo campos...")
        if df is not None:
            for _, row in df.iterrows():
                with st.expander(f"{row['FILE_NAME']}", expanded=True):
                    render_json(row["CAMPOS_EXTRAIDOS"])

    st.info(
        "**Insight:** los equipos legales y operaciones se ahorran horas. "
        "Cada campo se puede unir directamente con tu tabla de polizas."
    )

# =================================================================== Tab 3
with tab3:
    st.subheader("Ejercicio 3 - Audio con AI_TRANSCRIBE + AI_SENTIMENT + Coaching")
    st.markdown(
        "Tomamos llamadas reales, las **transcribimos**, medimos **sentimiento** "
        "y generamos **coaching** para el asesor."
    )

    try:
        audios = run_sql(
            "SELECT file_name, transcripcion, sentimiento "
            "FROM AI_SUMMIT.PUBLIC.TRANSCRIPCIONES"
        )
        urls = run_sql(
            "SELECT RELATIVE_PATH AS file_name, GET_PRESIGNED_URL(@AI_SUMMIT.PUBLIC.AUDIO, "
            "RELATIVE_PATH, 3600) AS URL FROM DIRECTORY(@AI_SUMMIT.PUBLIC.AUDIO)"
        )
        url_map = dict(zip(urls["FILE_NAME"], urls["URL"]))

        # Soporte/problema primero, ofrecimiento despues
        def _orden(name: str) -> int:
            n = (name or "").lower()
            if "problema" in n or "soporte" in n:
                return 0
            return 1

        audios = audios.sort_values(
            by="FILE_NAME", key=lambda s: s.map(_orden)
        ).reset_index(drop=True)

        cols = st.columns(max(1, len(audios)))
        for i, row in audios.iterrows():
            sent = (row["SENTIMIENTO"] or "").lower()
            color = {"positive": "green", "negative": "red", "mixed": "orange"}.get(
                sent, "gray"
            )
            with cols[i]:
                with st.container(border=True):
                    st.markdown(
                        f"**{row['FILE_NAME']}** - sentimiento: :{color}[**{sent}**]"
                    )
                    if row["FILE_NAME"] in url_map:
                        st.audio(url_map[row["FILE_NAME"]])
                    with st.expander("Ver transcripcion"):
                        st.write(row["TRANSCRIPCION"])
    except Exception as e:
        st.error(f"Error: {e}")

    st.divider()
    st.markdown("##### Generar coaching para el asesor (JSON formateado)")
    sql_coach_default = """SELECT
  file_name,
  TRY_PARSE_JSON(
    AI_COMPLETE(
      'claude-4-sonnet',
      CONCAT(
        'Eres un coach experto en servicio al cliente. Analiza esta transcripcion y genera recomendaciones para el asesor en formato JSON con: ',
        '{"puntos_dolor": [...], "fortalezas_asesor": [...], "areas_mejora": [...], "recomendacion_inmediata": "...", "script_sugerido": "frase exacta a usar en la proxima interaccion"}. ',
        'Responde SOLO el JSON valido, sin markdown ni backticks, en espanol. Transcripcion: ', transcripcion
      )
    )
  ) AS recomendaciones
FROM AI_SUMMIT.PUBLIC.TRANSCRIPCIONES;"""
    sql_coach = editable_sql("coach", sql_coach_default, height=240)

    if st.button("Generar coaching", key="btn_coach", type="primary"):
        df = safe_run(sql_coach, "Generando recomendaciones...")
        if df is not None:
            for _, row in df.iterrows():
                with st.expander(f"Coaching para {row['FILE_NAME']}", expanded=True):
                    render_json(row["RECOMENDACIONES"])

    st.info(
        "**Insight:** combinamos 3 funciones AI en SQL plano. "
        "Sin notebooks externos, sin mover audio."
    )

# =================================================================== Tab 4
with tab4:
    st.subheader("Ejercicio 4 - Cortex Code")
    st.markdown(
        "Para abrir **Cortex Code** haz clic en el **icono de la chispa** ubicado en la "
        "**esquina inferior derecha** de Snowsight. "
        "Asegurate de estar en `AI_SUMMIT.PUBLIC` con warehouse `AI_SUMMIT_WH`. "
        "Pega cada prompt y observa como Cortex Code genera el codigo."
    )

    prompts = [
        (
            "Vista que clasifica imagenes",
            "Crea una vista llamada V_IMAGENES_CLASIFICADAS que recorra todos los archivos "
            "del stage IMAGENES y agregue una columna con la clasificacion del tipo de imagen "
            "(cedula, accidente vehicular, factura, otro) usando AI_CLASSIFY sobre AI_COMPLETE multimodal.",
        ),
        (
            "Vista 360 unificada",
            "Crea una vista llamada V_HOL_360 que combine las filas de DOCS_PARSED y "
            "TRANSCRIPCIONES en un solo dataset con columnas: tipo_fuente, archivo, contenido, sentimiento.",
        ),
        (
            "Conversa con tus datos",
            "Genera un SELECT que invoque a AI_COMPLETE preguntandole: cuanto es el canon mensual "
            "del contrato numero 2 y cual fue el sentimiento de la ultima llamada?",
        ),
        (
            "App Streamlit dashboard",
            "Crea una app Streamlit in Snowflake llamada DASHBOARD_HOL que muestre el total de "
            "imagenes por tipo, el sentimiento de las llamadas en grafico de barras, y un campo "
            "de chat conectado al agente.",
        ),
    ]

    for i, (title, prompt) in enumerate(prompts, 1):
        with st.container(border=True):
            st.markdown(f"**Prompt {i} - {title}**")
            st.code(prompt, language="text")

    st.info(
        "**Insight:** una persona de negocio puede construir pipelines de IA productivos "
        "**sin esperar un sprint**."
    )

# =================================================================== Tab 5
with tab5:
    st.subheader("Ejercicio 5 - Cortex Analyst + Search + Agente")
    st.markdown(
        "Cerramos con el **Snowflake Intelligence Agent** que combina texto-a-SQL, "
        "busqueda semantica y graficos."
    )

    st.markdown("##### Cortex Analyst - preguntas en espanol sobre datos estructurados")
    sql_region_default = """SELECT region, SUM(prima_mensual) AS total_primas, COUNT(*) AS num_polizas
FROM AI_SUMMIT.PUBLIC.POLIZAS
WHERE estado = 'Activa'
GROUP BY region
ORDER BY total_primas DESC;"""
    sql_region = editable_sql("region", sql_region_default, height=140)

    if st.button("Ejecutar query", key="btn_region", type="primary"):
        df = safe_run(sql_region)
        if df is not None:
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.bar_chart(df.set_index("REGION")["TOTAL_PRIMAS"])

    st.divider()
    st.markdown("##### Cortex Search - busqueda semantica en contratos y llamadas")
    query = st.text_input("Tu busqueda:", value="cliente molesto sin servicio", key="search_q")
    sql_search_default = (
        "SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(\n"
        "  'AI_SUMMIT.PUBLIC.DOCS_SEARCH',\n"
        '  \'{"query": "<TU_BUSQUEDA>", "columns": ["contenido","file_name","tipo_documento"], "limit": 3}\'\n'
        ") AS R"
    )
    sql_search = editable_sql("search", sql_search_default, height=140)

    if st.button("Buscar", key="btn_search", type="primary"):
        sql = sql_search.replace("<TU_BUSQUEDA>", query.replace("'", ""))
        df = safe_run(sql, "Buscando...")
        if df is not None:
            try:
                res = df.iloc[0]["R"]
                data = json.loads(res) if isinstance(res, str) else res
                for hit in data.get("results", []):
                    with st.expander(
                        f"{hit.get('file_name', '?')} ({hit.get('tipo_documento', '?')})"
                    ):
                        st.write(hit.get("contenido", ""))
            except Exception as e:
                st.error(f"Error parseando resultados: {e}")

    st.divider()
    st.markdown("##### Snowflake Intelligence Agent")
    st.markdown(
        "El agente `AGENTE_SEGUROS_360` ya esta creado y combina los 3 tools: "
        "Cortex Analyst, Cortex Search y data_to_chart."
    )
    st.link_button(
        "Abrir el agente en Snowflake Intelligence",
        "https://ai.snowflake.com",
        type="primary",
        use_container_width=True,
    )

    st.success(
        "**Felicitaciones!** En 20 minutos pasaste de archivos crudos "
        "(imagenes, PDFs, audio) a un agente conversacional productivo."
    )
