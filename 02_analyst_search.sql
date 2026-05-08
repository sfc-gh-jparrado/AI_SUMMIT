-- =====================================================================
-- Workshop AI SUMMIT - 02 CORTEX ANALYST + CORTEX SEARCH
-- =====================================================================
-- ORDEN DE EJECUCION: archivo 3 de 4. Requiere 00_base.sql ya ejecutado.
-- Crea:
--   - Tabla BASE_CONOCIMIENTO (union de DOCS_PARSED + TRANSCRIPCIONES)
--   - CORTEX SEARCH SERVICE DOCS_SEARCH (indexa contratos + llamadas)
--   - SEMANTIC VIEW SV_SEGUROS (Cortex Analyst sobre POLIZAS, CLIENTES,
--     RECLAMACIONES, con verified queries)
-- Es la pieza mas pesada del setup (la indexacion del Search puede tomar
-- 30-60 segundos). Se puede ejecutar en paralelo con 01_streamlit.sql.
-- =====================================================================
-- DURATION: ~45s (Cortex Search indexing)
-- IDEMPOTENT: TRUE  (CREATE OR REPLACE)
-- ROLE_REQUIRED: ACCOUNTADMIN
-- DEPENDS_ON: 00_base.sql (DOCS_PARSED, TRANSCRIPCIONES, POLIZAS, CLIENTES, RECLAMACIONES)
-- =====================================================================

USE ROLE ACCOUNTADMIN;
USE DATABASE AI_SUMMIT;
USE SCHEMA PUBLIC;
USE WAREHOUSE AI_SUMMIT_WH;

-- ---------------------------------------------------------------------
-- 1. Cortex Search Service: contratos + transcripciones de llamadas
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE BASE_CONOCIMIENTO AS
SELECT file_name, 'Contrato' AS tipo_documento, content AS contenido FROM DOCS_PARSED
UNION ALL
SELECT file_name, 'Transcripción llamada', transcripcion FROM TRANSCRIPCIONES;

CREATE OR REPLACE CORTEX SEARCH SERVICE DOCS_SEARCH
  ON contenido
  ATTRIBUTES tipo_documento, file_name
  WAREHOUSE = AI_SUMMIT_WH
  TARGET_LAG = '1 hour'
  EMBEDDING_MODEL = 'snowflake-arctic-embed-l-v2.0'
AS (SELECT contenido, tipo_documento, file_name FROM BASE_CONOCIMIENTO);

-- ---------------------------------------------------------------------
-- 2. Semantic View para Cortex Analyst (datos estructurados)
-- ---------------------------------------------------------------------
CALL SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML('AI_SUMMIT.PUBLIC', $$
name: SV_SEGUROS
description: "Vista semántica de una empresa de seguros e inmobiliaria. Incluye pólizas vendidas, clientes y reclamaciones por siniestros."

tables:
  - name: polizas
    description: "Pólizas de seguros vendidas (hogar, vehicular, vida)"
    base_table:
      database: AI_SUMMIT
      schema: PUBLIC
      table: POLIZAS
    primary_key:
      columns:
        - ID
    dimensions:
      - name: tipo_poliza
        synonyms: ["tipo de seguro", "ramo", "línea de negocio"]
        description: "Tipo de póliza: Hogar, Vehicular o Vida"
        expr: tipo_poliza
        data_type: VARCHAR
        is_enum: true
        sample_values: ["Hogar", "Vehicular", "Vida"]
      - name: producto
        synonyms: ["plan", "nombre del producto"]
        description: "Nombre del producto de seguro específico"
        expr: producto
        data_type: VARCHAR
      - name: region
        synonyms: ["departamento", "zona"]
        description: "Región geográfica de Colombia"
        expr: region
        data_type: VARCHAR
        is_enum: true
        sample_values: ["Bogotá", "Antioquia", "Valle", "Santander", "Atlántico"]
      - name: ciudad
        description: "Ciudad donde se vendió la póliza"
        expr: ciudad
        data_type: VARCHAR
      - name: cliente
        synonyms: ["asegurado", "tomador"]
        description: "Nombre del cliente que adquirió la póliza"
        expr: cliente
        data_type: VARCHAR
      - name: vendedor
        synonyms: ["asesor", "agente"]
        description: "Nombre del vendedor o asesor comercial"
        expr: vendedor
        data_type: VARCHAR
      - name: estado
        description: "Estado de la póliza: Activa o Cancelada"
        expr: estado
        data_type: VARCHAR
        is_enum: true
        sample_values: ["Activa", "Cancelada"]
      - name: canal_venta
        synonyms: ["canal", "canal de adquisición"]
        description: "Canal por el cual se vendió: Telefónico, Digital, Presencial"
        expr: canal_venta
        data_type: VARCHAR
        is_enum: true
        sample_values: ["Telefónico", "Digital", "Presencial"]
    time_dimensions:
      - name: fecha
        synonyms: ["fecha de venta", "fecha emisión"]
        description: "Fecha en que se emitió la póliza"
        expr: fecha
        data_type: DATE
    facts:
      - name: prima_mensual
        synonyms: ["prima", "valor mensual", "cuota"]
        description: "Prima mensual que paga el cliente en pesos colombianos"
        expr: prima_mensual
        data_type: NUMBER
      - name: cobertura_total
        synonyms: ["valor asegurado", "cobertura", "suma asegurada"]
        description: "Monto total de cobertura de la póliza en pesos colombianos"
        expr: cobertura_total
        data_type: NUMBER
    metrics:
      - name: total_primas
        synonyms: ["ingresos por primas", "recaudo"]
        description: "Suma total de primas mensuales"
        expr: SUM(prima_mensual)
      - name: promedio_prima
        synonyms: ["prima promedio", "ticket promedio"]
        description: "Prima mensual promedio por póliza"
        expr: AVG(prima_mensual)
      - name: total_polizas
        synonyms: ["cantidad de pólizas", "pólizas vendidas"]
        description: "Número total de pólizas"
        expr: COUNT(*)
      - name: cobertura_promedio
        description: "Cobertura promedio por póliza"
        expr: AVG(cobertura_total)
    filters:
      - name: polizas_activas
        description: "Solo pólizas con estado Activa"
        expr: "estado = 'Activa'"
      - name: ultimo_trimestre
        description: "Pólizas emitidas en los últimos 3 meses"
        expr: "fecha >= DATEADD(month, -3, CURRENT_DATE())"

  - name: clientes
    description: "Clientes registrados en la aseguradora"
    base_table:
      database: AI_SUMMIT
      schema: PUBLIC
      table: CLIENTES
    primary_key:
      columns:
        - ID
    unique_keys:
      - columns:
          - NOMBRE
    dimensions:
      - name: nombre
        synonyms: ["nombre cliente", "asegurado"]
        description: "Nombre completo del cliente"
        expr: nombre
        data_type: VARCHAR
      - name: segmento
        synonyms: ["categoría cliente", "nivel"]
        description: "Segmento del cliente: Básico, Estándar, Premium, VIP"
        expr: segmento
        data_type: VARCHAR
        is_enum: true
        sample_values: ["Básico", "Estándar", "Premium", "VIP"]
      - name: ciudad_cliente
        synonyms: ["ciudad del cliente"]
        description: "Ciudad de residencia del cliente"
        expr: ciudad
        data_type: VARCHAR
      - name: region_cliente
        description: "Región del cliente"
        expr: region
        data_type: VARCHAR
      - name: canal_preferido
        description: "Canal preferido de contacto del cliente"
        expr: canal_preferido
        data_type: VARCHAR
        is_enum: true
        sample_values: ["Presencial", "Telefónico", "Digital"]
    time_dimensions:
      - name: fecha_registro
        description: "Fecha de registro del cliente"
        expr: fecha_registro
        data_type: DATE
    facts:
      - name: polizas_activas_cliente
        description: "Número de pólizas activas del cliente"
        expr: polizas_activas
        data_type: NUMBER
      - name: valor_total_primas_cliente
        description: "Valor total de primas mensuales del cliente"
        expr: valor_total_primas
        data_type: NUMBER
    metrics:
      - name: total_clientes
        description: "Número total de clientes"
        expr: COUNT(*)
      - name: ltv_promedio
        synonyms: ["valor promedio del cliente"]
        description: "Valor promedio de primas por cliente"
        expr: AVG(valor_total_primas)

  - name: reclamaciones
    description: "Reclamaciones y siniestros reportados por clientes"
    base_table:
      database: AI_SUMMIT
      schema: PUBLIC
      table: RECLAMACIONES
    primary_key:
      columns:
        - ID
    dimensions:
      - name: cliente_reclamacion
        synonyms: ["reclamante"]
        description: "Cliente que presenta la reclamación"
        expr: cliente
        data_type: VARCHAR
      - name: tipo_poliza_reclamacion
        description: "Tipo de póliza asociada a la reclamación"
        expr: tipo_poliza
        data_type: VARCHAR
      - name: tipo_siniestro
        synonyms: ["tipo de evento", "causa"]
        description: "Tipo de siniestro: Choque, Incendio, Robo, Inundación, Hospitalización"
        expr: tipo_siniestro
        data_type: VARCHAR
        is_enum: true
        sample_values: ["Choque", "Incendio", "Robo", "Inundación", "Hospitalización"]
      - name: estado_reclamacion
        synonyms: ["estado del caso"]
        description: "Estado: Aprobada, Rechazada, En proceso"
        expr: estado
        data_type: VARCHAR
        is_enum: true
        sample_values: ["Aprobada", "Rechazada", "En proceso"]
    time_dimensions:
      - name: fecha_reclamacion
        synonyms: ["fecha del siniestro"]
        description: "Fecha en que se reportó la reclamación"
        expr: fecha
        data_type: DATE
    facts:
      - name: monto_reclamado
        synonyms: ["valor reclamado"]
        description: "Monto solicitado por el cliente"
        expr: monto_reclamado
        data_type: NUMBER
      - name: monto_aprobado
        synonyms: ["valor aprobado", "indemnización"]
        description: "Monto aprobado para pago"
        expr: monto_aprobado
        data_type: NUMBER
      - name: dias_resolucion
        synonyms: ["tiempo de respuesta"]
        description: "Días que tomó resolver la reclamación"
        expr: dias_resolucion
        data_type: NUMBER
    metrics:
      - name: total_reclamaciones
        description: "Número total de reclamaciones"
        expr: COUNT(*)
      - name: monto_total_aprobado
        synonyms: ["total indemnizado"]
        description: "Suma total de montos aprobados"
        expr: SUM(monto_aprobado)
      - name: promedio_dias_resolucion
        synonyms: ["tiempo promedio de resolución"]
        description: "Promedio de días para resolver reclamaciones"
        expr: AVG(dias_resolucion)
      - name: tasa_aprobacion
        synonyms: ["porcentaje de aprobación"]
        description: "Porcentaje de reclamaciones aprobadas"
        expr: "COUNT(CASE WHEN estado = 'Aprobada' THEN 1 END) * 100.0 / COUNT(*)"

relationships:
  - name: polizas_a_clientes
    left_table: polizas
    right_table: clientes
    relationship_columns:
      - left_column: CLIENTE
        right_column: NOMBRE
    relationship_type: many_to_one
  - name: reclamaciones_a_clientes
    left_table: reclamaciones
    right_table: clientes
    relationship_columns:
      - left_column: CLIENTE
        right_column: NOMBRE
    relationship_type: many_to_one

verified_queries:
  - name: ventas_por_region
    question: "¿Cuál es el total de primas por región?"
    use_as_onboarding_question: true
    sql: |
      SELECT region, SUM(prima_mensual) AS total_primas, COUNT(*) AS num_polizas
      FROM AI_SUMMIT.PUBLIC.POLIZAS
      WHERE estado = 'Activa'
      GROUP BY region
      ORDER BY total_primas DESC
  - name: top_vendedores
    question: "¿Quiénes son los mejores vendedores?"
    use_as_onboarding_question: true
    sql: |
      SELECT vendedor, COUNT(*) AS polizas_vendidas, SUM(prima_mensual) AS total_primas
      FROM AI_SUMMIT.PUBLIC.POLIZAS
      WHERE estado = 'Activa'
      GROUP BY vendedor
      ORDER BY total_primas DESC
  - name: reclamaciones_pendientes
    question: "¿Cuántas reclamaciones están en proceso?"
    use_as_onboarding_question: true
    sql: |
      SELECT tipo_siniestro, cliente, monto_reclamado, fecha
      FROM AI_SUMMIT.PUBLIC.RECLAMACIONES
      WHERE estado = 'En proceso'
      ORDER BY monto_reclamado DESC
  - name: clientes_premium
    question: "¿Cuáles son los clientes premium y VIP?"
    sql: |
      SELECT nombre, segmento, ciudad, polizas_activas, valor_total_primas
      FROM AI_SUMMIT.PUBLIC.CLIENTES
      WHERE segmento IN ('Premium', 'VIP')
      ORDER BY valor_total_primas DESC
$$);

-- Grants para que el agente y la UI puedan consumirlos
GRANT SELECT ON SEMANTIC VIEW AI_SUMMIT.PUBLIC.SV_SEGUROS TO ROLE PUBLIC;
GRANT USAGE ON CORTEX SEARCH SERVICE AI_SUMMIT.PUBLIC.DOCS_SEARCH TO ROLE PUBLIC;

-- ---------------------------------------------------------------------
-- Confirmacion
-- ---------------------------------------------------------------------
SELECT '02_analyst_search.sql completado' AS status,
       'Cortex Analyst: AI_SUMMIT.PUBLIC.SV_SEGUROS' AS analyst,
       'Cortex Search: AI_SUMMIT.PUBLIC.DOCS_SEARCH' AS search,
       'Siguiente: 03_agent.sql' AS siguiente;
