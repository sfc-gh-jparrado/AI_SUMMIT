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


# CSS minimo para que el boton de copiar de st.code sea siempre visible y oscuro
st.markdown(
    """
    <style>
    div[data-testid="stCodeBlock"] button,
    div[data-testid="stCode"] button,
    pre button {
        opacity: 1 !important;
        color: #11567F !important;
        background-color: #FFFFFF !important;
        border: 1px solid #11567F !important;
    }
    div[data-testid="stCodeBlock"] button svg,
    div[data-testid="stCode"] button svg,
    pre button svg {
        color: #11567F !important;
        fill: #11567F !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================== helpers
def run_sql(sql: str):
    """Run SQL and return pandas DataFrame."""
    return session.sql(sql).to_pandas()


def editable_sql(key: str, default_sql: str, height: int = 200) -> str:
    """Render an editable SQL block. The Restaurar Query button se renderiza
    aparte via run_query_buttons(key) para alinearlo al lado de Ejecutar Query.
    """
    state_key = f"sql_{key}"
    reset_flag = f"reset_{key}_flag"

    # Apply pending reset BEFORE the widget is created
    if st.session_state.get(reset_flag):
        st.session_state[state_key] = default_sql
        st.session_state[reset_flag] = False

    if state_key not in st.session_state:
        st.session_state[state_key] = default_sql

    st.caption(":blue[SQL editable] - modificalo libremente. Si rompes algo, usa Restaurar Query.")
    edited = st.text_area(
        "SQL editable",
        key=state_key,
        height=height,
        label_visibility="collapsed",
    )
    return edited


def _set_default(default_sql_for_key: dict, key: str, sql: str):
    """Helper interno: registra el SQL default para reset."""
    default_sql_for_key[key] = sql


def run_query_buttons(key: str, run_label: str = "Ejecutar Query") -> bool:
    """Renderiza dos botones lado a lado: Ejecutar Query (azul, izquierda) y
    Restaurar Query (gris, a la derecha, mismo tamaño). Devuelve True si se
    hizo click en Ejecutar.
    """
    reset_flag = f"reset_{key}_flag"

    def _request_reset():
        st.session_state[reset_flag] = True

    cols = st.columns([1, 1, 4])
    with cols[0]:
        clicked = st.button(run_label, key=f"btn_{key}", type="primary", use_container_width=True)
    with cols[1]:
        st.button(
            "Restaurar Query",
            key=f"btn_reset_{key}",
            on_click=_request_reset,
            type="secondary",
            icon=":material/restart_alt:",
            use_container_width=True,
        )
    return clicked


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
tab0, tab1, tab2, tab3, tab6, tab4, tab5 = st.tabs(
    [
        "Bienvenida",
        "Imagenes",
        "Documentos",
        "Audio",
        "Mas AI Functions",
        "Cortex Code",
        "Agente",
    ]
)

# =================================================================== Tab 0
with tab0:
    st.subheader("Bienvenido al Workshop AI Summit")
    st.markdown(
        "Ahora vamos a hacer en **menos de 15 minutos** lo que normalmente toma "
        "**semanas a un equipo** de integraciones, modelos y pipelines. Trabajamos con "
        "datos reales de una empresa **de seguros e inmobiliaria en Colombia** y al "
        "final tendras un **agente conversacional** listo para tus datos."
    )
    st.markdown(
        "**Lo unico que vas a usar es SQL**: nada de aplicaciones externas, sin mover archivos, "
        "sin entrenar modelos. Todo corre dentro de Snowflake."
    )

    st.divider()
    st.markdown("#### Lo que vas a hacer")

    pasos = [
        (
            "Imagenes con IA multimodal",
            "Le entregas a **Claude-4 Sonnet** la foto de un **siniestro vehicular** y una "
            "**cedula**. En una sola consulta obtienes el peritaje del dano (severidad y "
            "costo estimado) y los datos del cliente para verificar su identidad.",
        ),
        (
            "Documentos a datos estructurados",
            "Tomamos **contratos de arrendamiento en PDF** y con `AI_EXTRACT` sacamos "
            "**arrendador, canon, plazo, direccion del inmueble y poliza**, listos para "
            "tu data warehouse. Adios al data entry manual.",
        ),
        (
            "Audio: transcripcion + sentimiento + coaching",
            "Llamadas reales del contact center se convierten a texto con `AI_TRANSCRIBE`, "
            "medimos el sentimiento del cliente con `AI_SENTIMENT` y `AI_COMPLETE` genera "
            "**coaching automatico** para el asesor (puntos de dolor, fortalezas, script sugerido).",
        ),
        (
            "Cortex Code",
            "Le pides en lenguaje natural lo que necesitas (una vista, una app Streamlit, "
            "una clasificacion) y **Cortex Code escribe el SQL por ti**, directo en Snowsight.",
        ),
        (
            "Snowflake Intelligence Agent",
            "Cerramos con el agente **AGENTE_SEGUROS_360** que combina **Cortex Analyst** "
            "(texto-a-SQL sobre polizas, clientes y reclamaciones), **Cortex Search** "
            "(contratos + transcripciones) y graficos automaticos.",
        ),
        (
            "Mas AI Functions",
            "Veras **AI_FILTER, AI_REDACT, AI_AGG y AI_CLASSIFY** en accion: filtros "
            "inteligentes, anonimizacion de PII, resumenes consolidados y clasificacion. "
            "Mas una tabla con muchas mas funciones disponibles en SQL.",
        ),
    ]

    for titulo, desc in pasos:
        with st.container(border=True):
            st.markdown(f"**:blue[{titulo}]**")
            st.markdown(desc)

    st.info(
        "Avanza a la pestana **Imagenes** para empezar. Cada query es "
        "editable: si rompes algo, usa el boton **Restaurar**."
    )

# =================================================================== Tab 1
with tab1:
    st.subheader("Imagenes con IA Multimodal")
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

    if run_query_buttons("choque"):
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

    if run_query_buttons("cedula"):
        df = safe_run(sql_cedula, "Extrayendo campos...")
        if df is not None:
            st.success("Extraccion completada")
            render_json(df.iloc[0]["DATOS_CEDULA"])

    st.info(
        "**Insight competitivo:** lo que ves se hizo en **una sola consulta SQL**. "
        "Procesos tradicionales de OCR + parsing + validacion toman semanas y multiples "
        "servicios externos; aqui un perito digital y la verificacion de identidad estan "
        "resueltos en minutos.\n\n**Imagina procesar** los documentos o imagenes en tu empresa "
        "asi (siniestros, verificacion de identidad, facturas, evidencias)."
    )

# =================================================================== Tab 2
with tab2:
    st.subheader("Documentos a datos estructurados")
    st.markdown(
        "Snowflake procesa **PDF, DOCX, PPTX y mas** sin pre-procesar. "
        "Convertimos contratos legales en datos consumibles."
    )

    st.markdown("##### Contratos disponibles - descarga el PDF original")
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

    if run_query_buttons("extract_docs"):
        df = safe_run(sql_extract, "Extrayendo campos...")
        if df is not None:
            for _, row in df.iterrows():
                with st.expander(f"{row['FILE_NAME']}", expanded=True):
                    render_json(row["CAMPOS_EXTRAIDOS"])

    st.info(
        "**Insight competitivo:** equipos legales y operaciones suelen invertir **horas por contrato** "
        "leyendo y digitando datos. Snowflake los convierte en columnas listas para tu tabla de "
        "polizas en **una linea de SQL**.\n\n**Imagina procesar** todos los PDFs (contratos, "
        "polizas, ordenes de compra, actas) que tienes pendientes en tu organizacion en una sola tarde."
    )

# =================================================================== Tab 3
with tab3:
    st.subheader("Audio con AI_TRANSCRIBE + AI_SENTIMENT + Coaching")
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
    st.markdown("##### Como se generaron esas transcripciones (AI_TRANSCRIBE)")
    st.caption(
        "Las transcripciones que ves arriba se hidrataron en el setup para acelerar el "
        "workshop. Asi se obtienen en vivo desde el audio crudo:"
    )
    sql_transcribe_default = """SELECT
  AI_TRANSCRIBE(
    TO_FILE('@AI_SUMMIT.PUBLIC.AUDIO', 'problema-servicio.mp3')
  ) AS transcripcion;"""
    sql_transcribe = editable_sql("transcribe", sql_transcribe_default, height=120)

    if run_query_buttons("transcribe"):
        df = safe_run(sql_transcribe, "Transcribiendo audio...")
        if df is not None:
            with st.container(border=True):
                render_json(df.iloc[0]["TRANSCRIPCION"])

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

    if run_query_buttons("coach"):
        df = safe_run(sql_coach, "Generando recomendaciones...")
        if df is not None:
            for _, row in df.iterrows():
                with st.expander(f"Coaching para {row['FILE_NAME']}", expanded=True):
                    render_json(row["RECOMENDACIONES"])

    st.info(
        "**Insight competitivo:** transcribir, medir sentimiento y generar coaching "
        "normalmente requiere 3 herramientas distintas, integraciones y mover audio entre "
        "clouds. Aqui es **SQL puro sobre el archivo en su lugar**, sin pipelines.\n\n"
        "**Imagina procesar** todas las llamadas de tu contact center, reuniones de venta o "
        "entrevistas y entenderlas automaticamente esta semana."
    )

# =================================================================== Tab 4
with tab4:
    st.subheader("Cortex Code")
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
        "**Insight competitivo:** lo que toma a un equipo dias de desarrollo (vistas, queries, "
        "apps), Cortex Code lo escribe en segundos directo en Snowsight. **Sin sprints, sin "
        "tickets, sin esperar.** **Piensa:** que vista, dashboard o pipeline llevas semanas "
        "esperando que alguien construya en tu empresa?"
    )

# =================================================================== Tab 5
with tab5:
    st.subheader("Cortex Analyst + Search + Agente")
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

    if run_query_buttons("region"):
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

    if run_query_buttons("search"):
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
        "(imagenes, PDFs, audio) a un agente conversacional productivo. "
        "**El proximo paso es tuyo:** lleva uno de estos casos a tu organizacion esta semana."
    )

# =================================================================== Tab 6 (Mas AI Functions)
with tab6:
    st.subheader("Mas AI Functions de Snowflake Cortex")
    st.markdown(
        "Mas alla de `AI_COMPLETE`, `AI_EXTRACT`, `AI_TRANSCRIBE` y `AI_SENTIMENT` "
        "que ya viste, **Snowflake Cortex** trae una bateria de funciones SQL "
        "especializadas. Aqui hay 4 ejemplos listos para correr."
    )

    # ---------- AI_FILTER ----------
    st.divider()
    st.markdown("##### 1. AI_FILTER - filtrar filas con lenguaje natural")
    st.caption(
        "Devuelve TRUE/FALSE segun una condicion en lenguaje natural. "
        "Reemplaza WHERE complicados por preguntas de negocio."
    )
    sql_filter_default = """SELECT file_name, sentimiento, LEFT(transcripcion, 200) AS preview
FROM AI_SUMMIT.PUBLIC.TRANSCRIPCIONES
WHERE AI_FILTER(
  PROMPT('En la siguiente transcripcion de una llamada al servicio al cliente, el cliente esta molesto, frustrado o tiene un problema sin resolver? Responde TRUE solo si el cliente expresa insatisfaccion, queja o problema activo. Transcripcion: {0}', transcripcion)
);"""
    sql_filter = editable_sql("ai_filter", sql_filter_default, height=160)
    if run_query_buttons("ai_filter"):
        df = safe_run(sql_filter, "Filtrando con AI...")
        if df is not None:
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ---------- AI_REDACT ----------
    st.divider()
    st.markdown("##### 2. AI_REDACT - anonimizar PII")
    st.caption(
        "Detecta y reemplaza datos personales (nombres, telefonos, correos, IDs) "
        "directamente en SQL. Critico para gobernanza, compartir datos y compliance."
    )
    sql_redact_default = """SELECT
  file_name,
  AI_REDACT(LEFT(content, 1500), ['NAME', 'NATIONAL_ID', 'ADDRESS']) AS contenido_anonimizado
FROM AI_SUMMIT.PUBLIC.DOCS_PARSED;"""
    sql_redact = editable_sql("ai_redact", sql_redact_default, height=140)
    if run_query_buttons("ai_redact"):
        df = safe_run(sql_redact, "Anonimizando...")
        if df is not None:
            for _, row in df.iterrows():
                with st.expander(f"{row['FILE_NAME']}", expanded=True):
                    st.write(row["CONTENIDO_ANONIMIZADO"])

    # ---------- AI_AGG ----------
    st.divider()
    st.markdown("##### 3. AI_AGG - resumir / razonar sobre muchas filas")
    st.caption(
        "Equivalente a SUM/AVG pero sobre texto: una instruccion en lenguaje natural "
        "se aplica a todas las filas y devuelve un solo resultado consolidado."
    )
    sql_agg_default = """SELECT AI_AGG(
  transcripcion,
  'Eres un analista de calidad de servicio. Resume en espanol los temas comunes, las quejas mas frecuentes y las oportunidades de mejora detectadas en estas llamadas.'
) AS resumen_consolidado
FROM AI_SUMMIT.PUBLIC.TRANSCRIPCIONES;"""
    sql_agg = editable_sql("ai_agg", sql_agg_default, height=160)
    if run_query_buttons("ai_agg"):
        df = safe_run(sql_agg, "Consolidando insights...")
        if df is not None:
            st.write(df.iloc[0]["RESUMEN_CONSOLIDADO"])

    # ---------- AI_CLASSIFY ----------
    st.divider()
    st.markdown("##### 4. AI_CLASSIFY - clasificar texto en categorias")
    st.caption(
        "Asigna a cada texto la categoria mas adecuada de una lista que tu defines. "
        "Sin entrenar modelos ni etiquetar datos."
    )
    sql_classify_default = """SELECT
  file_name,
  AI_CLASSIFY(
    content,
    ['contrato_vivienda', 'contrato_comercial', 'contrato_industrial', 'otro']
  ):labels[0]::STRING AS tipo_contrato
FROM AI_SUMMIT.PUBLIC.DOCS_PARSED;"""
    sql_classify = editable_sql("ai_classify", sql_classify_default, height=160)
    if run_query_buttons("ai_classify"):
        df = safe_run(sql_classify, "Clasificando...")
        if df is not None:
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ---------- Tabla de mas funciones ----------
    st.divider()
    st.markdown("##### Y muchas mas funciones AI en SQL")
    st.markdown(
        "Snowflake Cortex incluye una libreria amplia. Estas son las que **no** "
        "viste en el workshop, todas invocables como una funcion SQL mas."
    )
    mas_funciones = [
        ("AI_COMPLETE", "Llamada generica a un LLM (Claude, GPT, Llama, Mistral). Texto e imagenes."),
        ("AI_EXTRACT", "Extrae campos estructurados desde texto, imagenes o documentos."),
        ("AI_SENTIMENT", "Mide sentimiento (positivo/negativo/mixto) de un texto."),
        ("AI_TRANSCRIBE", "Transcribe audio y video a texto, con timestamps y speaker diarization."),
        ("AI_PARSE_DOCUMENT", "OCR + layout: extrae texto e imagenes de PDFs, DOCX, PPTX y mas."),
        ("AI_TRANSLATE", "Traduce entre idiomas soportados, en SQL."),
        ("AI_SUMMARIZE_AGG", "Resume una columna de texto a traves de muchas filas (sin limites de contexto)."),
        ("AI_EMBED", "Genera embeddings vectoriales para busqueda semantica y clustering."),
        ("AI_SIMILARITY", "Calcula similitud entre dos textos o imagenes (cosine/dot)."),
        ("AI_COUNT_TOKENS", "Cuenta tokens antes de una llamada para estimar costo."),
        ("PROMPT", "Helper para construir prompts dinamicos con columnas y archivos."),
        ("TO_FILE", "Crea una referencia a un archivo en stage para usar con AI_COMPLETE multimodal."),
        ("TRY_COMPLETE", "Como AI_COMPLETE pero devuelve NULL en error en vez de fallar el query."),
    ]
    import pandas as _pd
    df_funcs = _pd.DataFrame(mas_funciones, columns=["Funcion", "Que hace"])
    st.dataframe(df_funcs, use_container_width=True, hide_index=True)

    st.markdown(
        "**Modelos disponibles para `AI_COMPLETE`:** Claude (Sonnet 4, Opus 4, Haiku), "
        "GPT-5, GPT-5-mini, GPT-4.1, Llama 3.1/3.3 (8b, 70b, 405b), Mistral Large 2, "
        "Mixtral 8x7b, DeepSeek R1, Gemini 3.1 Pro y mas."
    )
    st.link_button(
        "Ver el catalogo completo en la documentacion oficial",
        "https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql#regional-availability",
        icon=":material/open_in_new:",
    )

    st.info(
        "**Insight competitivo:** todas estas funciones son **SQL plano** - no hay "
        "infraestructura, ni notebooks, ni mover datos.\n\n**Imagina procesar** filtros "
        "inteligentes, anonimizacion masiva, clasificacion de documentos y "
        "resumenes de miles de llamadas en una sola consulta."
    )
