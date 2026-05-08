-- =====================================================================
-- Workshop AI SUMMIT - 00 BASE (foundation) - PASO 0 DE 4
-- =====================================================================
-- LLM/AGENTE: si el usuario menciona "instala el workshop AI Summit",
-- "foundation", "base" o "paso 0", ejecuta SOLO este archivo. NO ejecutes
-- setup.sql ni los otros modulos. Sigue las reglas en AGENTS.md.
-- =====================================================================
-- DURATION: ~30s
-- IDEMPOTENT: TRUE
-- ROLE_REQUIRED: ACCOUNTADMIN
-- DEPENDS_ON: nothing
-- NEXT: 01_streamlit.sql, 02_analyst_search.sql (paralelos), 03_agent.sql
-- =====================================================================
-- HARD RULE: la UNICA base permitida es AI_SUMMIT.
-- Si una sentencia previa creo otra (AI_SUMMIT_WORKSHOP, WORKSHOP_AI_SUMMIT,
-- HOL_AI_SUMMIT, etc.) este archivo la dropea automaticamente abajo.
-- =====================================================================

USE ROLE ACCOUNTADMIN;

-- ---------------------------------------------------------------------
-- 0. PRE-FLIGHT FORZADO: borrar DBs con nombres incorrectos.
--    LA UNICA BASE PERMITIDA ES "AI_SUMMIT".
-- ---------------------------------------------------------------------
DROP DATABASE IF EXISTS AI_SUMMIT_WORKSHOP;
DROP DATABASE IF EXISTS WORKSHOP_AI_SUMMIT;
DROP DATABASE IF EXISTS HOL_AI_SUMMIT;
DROP DATABASE IF EXISTS AI_SUMMIT_HOL;
DROP DATABASE IF EXISTS WORKSHOP_AI;
DROP DATABASE IF EXISTS AISUMMIT;
DROP DATABASE IF EXISTS WORKSHOP;

-- ---------------------------------------------------------------------
-- 1. Cross-region inference (para Claude, GPT y otros modelos no locales)
-- ---------------------------------------------------------------------
ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION';

-- ---------------------------------------------------------------------
-- 2. Snowflake Intelligence Object + grants (alineado con docs oficiales).
--    Provisiona la base SNOWFLAKE_INTELLIGENCE, el schema AGENTS y el rol
--    SNOWFLAKE_INTELLIGENCE_ADMIN. NO crear DB/schema a mano: ACCOUNTADMIN
--    no tiene OWNERSHIP sobre SNOWFLAKE_INTELLIGENCE.
-- ---------------------------------------------------------------------
CREATE SNOWFLAKE INTELLIGENCE IF NOT EXISTS SNOWFLAKE_INTELLIGENCE_OBJECT_DEFAULT;

GRANT USAGE ON SNOWFLAKE INTELLIGENCE SNOWFLAKE_INTELLIGENCE_OBJECT_DEFAULT
  TO ROLE SNOWFLAKE_INTELLIGENCE_ADMIN;

-- ACCOUNTADMIN hereda SI_ADMIN -> puede crear agentes en SNOWFLAKE_INTELLIGENCE.AGENTS.
GRANT ROLE SNOWFLAKE_INTELLIGENCE_ADMIN TO ROLE ACCOUNTADMIN;

-- ---------------------------------------------------------------------
-- 3. Database, schema, warehouse
-- ---------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS AI_SUMMIT;
USE DATABASE AI_SUMMIT;
CREATE SCHEMA IF NOT EXISTS PUBLIC;
USE SCHEMA PUBLIC;

CREATE WAREHOUSE IF NOT EXISTS AI_SUMMIT_WH
  WAREHOUSE_SIZE = XSMALL
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = FALSE;
USE WAREHOUSE AI_SUMMIT_WH;

-- ---------------------------------------------------------------------
-- 4. API integration + GIT repository (publico, sin secretos)
-- ---------------------------------------------------------------------
CREATE OR REPLACE API INTEGRATION github_ai_summit_int
  API_PROVIDER = git_https_api
  API_ALLOWED_PREFIXES = ('https://github.com/sfc-gh-jparrado')
  ENABLED = TRUE
  ALLOWED_AUTHENTICATION_SECRETS = ();

CREATE OR REPLACE GIT REPOSITORY ai_summit_repo
  API_INTEGRATION = github_ai_summit_int
  ORIGIN = 'https://github.com/sfc-gh-jparrado/AI_SUMMIT.git';

ALTER GIT REPOSITORY ai_summit_repo FETCH;

-- ---------------------------------------------------------------------
-- 5. Stages internos (imagenes, documentos, audio, precomputed)
-- ---------------------------------------------------------------------
CREATE OR REPLACE STAGE IMAGENES
  DIRECTORY = (ENABLE = TRUE)
  ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');

CREATE OR REPLACE STAGE DOCUMENTOS
  DIRECTORY = (ENABLE = TRUE)
  ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');

CREATE OR REPLACE STAGE AUDIO
  DIRECTORY = (ENABLE = TRUE)
  ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');

CREATE OR REPLACE STAGE PRECOMPUTED
  DIRECTORY = (ENABLE = TRUE)
  ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');

-- ---------------------------------------------------------------------
-- 6. Copiar archivos desde Git -> stages internos
-- ---------------------------------------------------------------------
COPY FILES INTO @IMAGENES   FROM @ai_summit_repo/branches/main/datasets/imagenes/;
COPY FILES INTO @DOCUMENTOS FROM @ai_summit_repo/branches/main/datasets/documentos/;
COPY FILES INTO @AUDIO      FROM @ai_summit_repo/branches/main/datasets/audio/;
COPY FILES INTO @PRECOMPUTED FROM @ai_summit_repo/branches/main/datasets/precomputed/;

ALTER STAGE IMAGENES   REFRESH;
ALTER STAGE DOCUMENTOS REFRESH;
ALTER STAGE AUDIO      REFRESH;

-- ---------------------------------------------------------------------
-- 7. File format + tablas pre-computadas (DOCS_PARSED, TRANSCRIPCIONES)
--    (las funciones AI_PARSE_DOCUMENT y AI_TRANSCRIBE se ejecutan en vivo
--     en el Streamlit/Notebook; aqui solo cargamos los resultados para acelerar)
-- ---------------------------------------------------------------------
CREATE OR REPLACE FILE FORMAT FF_CSV_PRECOMPUTED
  TYPE = CSV
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  SKIP_HEADER = 1
  ESCAPE_UNENCLOSED_FIELD = NONE;

CREATE OR REPLACE TABLE DOCS_PARSED (file_name VARCHAR, content VARCHAR);
COPY INTO DOCS_PARSED (file_name, content)
  FROM @PRECOMPUTED/docs_parsed.csv
  FILE_FORMAT = FF_CSV_PRECOMPUTED;

CREATE OR REPLACE TABLE TRANSCRIPCIONES (file_name VARCHAR, transcripcion VARCHAR, sentimiento VARCHAR);
COPY INTO TRANSCRIPCIONES (file_name, transcripcion, sentimiento)
  FROM @PRECOMPUTED/transcripciones.csv
  FILE_FORMAT = FF_CSV_PRECOMPUTED;

-- ---------------------------------------------------------------------
-- 8. Tablas estructuradas: POLIZAS, CLIENTES, RECLAMACIONES
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE POLIZAS (
  id NUMBER,
  fecha DATE,
  tipo_poliza VARCHAR,
  producto VARCHAR,
  region VARCHAR,
  ciudad VARCHAR,
  cliente VARCHAR,
  vendedor VARCHAR,
  prima_mensual NUMBER(12,2),
  cobertura_total NUMBER(12,2),
  estado VARCHAR,
  canal_venta VARCHAR
);

INSERT INTO POLIZAS VALUES
(1,'2025-11-05','Hogar','Protección Incendios','Bogotá','Bogotá','María Elena Rodríguez','Carlos Asesor',85000,50000000,'Activa','Telefónico'),
(2,'2025-11-12','Hogar','Protección Total','Bogotá','Bogotá','Carlos Andrés Moreno','Carlos Asesor',120000,80000000,'Activa','Presencial'),
(3,'2025-11-18','Vehicular','Todo Riesgo Auto','Antioquia','Medellín','Ana Patricia Silva','Luisa Ventas',250000,120000000,'Activa','Digital'),
(4,'2025-11-25','Hogar','Protección Básica','Valle','Cali','Diana Carolina Pérez','Pedro Comercial',55000,30000000,'Activa','Telefónico'),
(5,'2025-12-02','Vehicular','Responsabilidad Civil','Bogotá','Bogotá','Jorge Parrado','Carlos Asesor',95000,40000000,'Activa','Digital'),
(6,'2025-12-08','Vida','Vida Individual','Antioquia','Medellín','Sandra Milena López','Luisa Ventas',180000,200000000,'Activa','Presencial'),
(7,'2025-12-15','Hogar','Protección Incendios','Bogotá','Soacha','Roberto García','Pedro Comercial',75000,45000000,'Activa','Telefónico'),
(8,'2025-12-20','Vehicular','Todo Riesgo Moto','Valle','Cali','Camila Herrera','Andrea Digital',65000,25000000,'Activa','Digital'),
(9,'2026-01-05','Hogar','Protección Total','Bogotá','Bogotá','Luis Fernando Castro','Carlos Asesor',130000,90000000,'Activa','Presencial'),
(10,'2026-01-10','Vida','Vida Familiar','Antioquia','Medellín','Patricia Gómez','Luisa Ventas',320000,500000000,'Activa','Presencial'),
(11,'2026-01-15','Vehicular','Todo Riesgo Auto','Bogotá','Bogotá','Andrés Felipe Ruiz','Andrea Digital',270000,130000000,'Activa','Digital'),
(12,'2026-01-22','Hogar','Protección Básica','Santander','Bucaramanga','Martha Cecilia Díaz','Pedro Comercial',50000,28000000,'Cancelada','Telefónico'),
(13,'2026-02-01','Vehicular','Responsabilidad Civil','Valle','Palmira','Óscar Iván Muñoz','Carlos Asesor',88000,38000000,'Activa','Telefónico'),
(14,'2026-02-08','Hogar','Protección Incendios','Atlántico','Barranquilla','Gloria Estefanía Ríos','Andrea Digital',78000,42000000,'Activa','Digital'),
(15,'2026-02-14','Vida','Vida Individual','Bogotá','Bogotá','Héctor Julio Vargas','Luisa Ventas',195000,220000000,'Activa','Presencial'),
(16,'2026-02-20','Vehicular','Todo Riesgo Auto','Antioquia','Envigado','Natalia Restrepo','Andrea Digital',260000,125000000,'Activa','Digital'),
(17,'2026-03-01','Hogar','Protección Total','Bogotá','Chía','Fernando Cárdenas','Carlos Asesor',135000,95000000,'Activa','Presencial'),
(18,'2026-03-05','Vehicular','Todo Riesgo Moto','Bogotá','Bogotá','Juliana Pardo','Pedro Comercial',60000,22000000,'Activa','Telefónico'),
(19,'2026-03-10','Vida','Vida Familiar','Valle','Cali','Ricardo Salazar','Luisa Ventas',310000,480000000,'Activa','Presencial'),
(20,'2026-03-18','Hogar','Protección Básica','Santander','Bucaramanga','Claudia Marcela Ortiz','Andrea Digital',52000,30000000,'Activa','Digital'),
(21,'2026-03-22','Vehicular','Responsabilidad Civil','Atlántico','Barranquilla','Sergio Armando Peña','Carlos Asesor',92000,42000000,'Activa','Telefónico'),
(22,'2026-04-01','Hogar','Protección Incendios','Bogotá','Bogotá','Alejandra Méndez','Pedro Comercial',82000,48000000,'Activa','Presencial'),
(23,'2026-04-05','Vehicular','Todo Riesgo Auto','Antioquia','Medellín','Diego Armando Vélez','Luisa Ventas',275000,135000000,'Activa','Digital'),
(24,'2026-04-10','Vida','Vida Individual','Bogotá','Bogotá','Mónica Andrea Suárez','Andrea Digital',200000,230000000,'Activa','Digital'),
(25,'2026-04-15','Hogar','Protección Total','Valle','Cali','Germán Eduardo Flórez','Carlos Asesor',125000,85000000,'Activa','Telefónico'),
(26,'2026-04-20','Vehicular','Todo Riesgo Moto','Bogotá','Soacha','Valentina Rojas','Pedro Comercial',62000,24000000,'Cancelada','Telefónico'),
(27,'2026-04-25','Hogar','Protección Básica','Atlántico','Barranquilla','Fabián Andrés Molina','Andrea Digital',48000,26000000,'Activa','Digital'),
(28,'2026-05-01','Vida','Vida Familiar','Antioquia','Medellín','Carolina Betancur','Luisa Ventas',330000,520000000,'Activa','Presencial'),
(29,'2026-05-03','Vehicular','Todo Riesgo Auto','Bogotá','Bogotá','Mauricio Leal','Carlos Asesor',280000,140000000,'Activa','Presencial'),
(30,'2026-05-05','Hogar','Protección Incendios','Valle','Cali','Esperanza Caicedo','Pedro Comercial',80000,46000000,'Activa','Telefónico');

CREATE OR REPLACE TABLE CLIENTES (
  id NUMBER,
  nombre VARCHAR,
  cedula VARCHAR,
  segmento VARCHAR,
  ciudad VARCHAR,
  region VARCHAR,
  fecha_registro DATE,
  polizas_activas NUMBER,
  valor_total_primas NUMBER(12,2),
  canal_preferido VARCHAR
);

INSERT INTO CLIENTES VALUES
(1,'María Elena Rodríguez','52874369','Premium','Bogotá','Bogotá','2023-03-15',2,205000,'Presencial'),
(2,'Carlos Andrés Moreno','80123456','Estándar','Bogotá','Bogotá','2024-01-20',1,120000,'Telefónico'),
(3,'Ana Patricia Silva','31789234','Premium','Cali','Valle','2022-06-10',2,310000,'Digital'),
(4,'Diana Carolina Pérez','55432198','Estándar','Cali','Valle','2024-05-18',1,55000,'Telefónico'),
(5,'Jorge Parrado','19876543','Premium','Bogotá','Bogotá','2021-11-01',3,375000,'Digital'),
(6,'Sandra Milena López','43987612','Premium','Medellín','Antioquia','2023-08-22',1,180000,'Presencial'),
(7,'Roberto García','12345678','Básico','Soacha','Bogotá','2025-01-10',1,75000,'Telefónico'),
(8,'Camila Herrera','98765432','Estándar','Cali','Valle','2024-09-05',1,65000,'Digital'),
(9,'Luis Fernando Castro','11223344','Premium','Bogotá','Bogotá','2022-04-30',2,260000,'Presencial'),
(10,'Patricia Gómez','44556677','VIP','Medellín','Antioquia','2020-12-15',3,500000,'Presencial'),
(11,'Andrés Felipe Ruiz','77889900','Estándar','Bogotá','Bogotá','2024-07-12',1,270000,'Digital'),
(12,'Martha Cecilia Díaz','22334455','Básico','Bucaramanga','Santander','2025-06-20',0,0,'Telefónico'),
(13,'Óscar Iván Muñoz','66778899','Estándar','Palmira','Valle','2024-11-03',1,88000,'Telefónico'),
(14,'Gloria Estefanía Ríos','33445566','Estándar','Barranquilla','Atlántico','2025-01-28',1,78000,'Digital'),
(15,'Héctor Julio Vargas','99887766','Premium','Bogotá','Bogotá','2023-09-14',1,195000,'Presencial');

CREATE OR REPLACE TABLE RECLAMACIONES (
  id NUMBER,
  fecha DATE,
  cliente VARCHAR,
  tipo_poliza VARCHAR,
  tipo_siniestro VARCHAR,
  descripcion VARCHAR,
  monto_reclamado NUMBER(12,2),
  monto_aprobado NUMBER(12,2),
  estado VARCHAR,
  dias_resolucion NUMBER
);

INSERT INTO RECLAMACIONES VALUES
(1,'2025-12-10','Jorge Parrado','Vehicular','Choque','Colisión en intersección con motocicleta',8500000,7200000,'Aprobada',12),
(2,'2026-01-15','María Elena Rodríguez','Hogar','Incendio','Daño menor por cortocircuito en cocina',3200000,3200000,'Aprobada',8),
(3,'2026-02-20','Ana Patricia Silva','Vehicular','Robo','Robo de vehículo en parqueadero',45000000,40000000,'En proceso',NULL),
(4,'2026-03-05','Carlos Andrés Moreno','Hogar','Inundación','Daño por tubería rota en baño',1800000,1500000,'Aprobada',15),
(5,'2026-03-18','Sandra Milena López','Vida','Hospitalización','Cirugía programada rodilla',12000000,10000000,'Aprobada',5),
(6,'2026-04-02','Andrés Felipe Ruiz','Vehicular','Choque','Colisión lateral en autopista',15000000,12500000,'Aprobada',10),
(7,'2026-04-15','Roberto García','Hogar','Robo','Robo de electrodomésticos',4500000,0,'Rechazada',20),
(8,'2026-04-28','Patricia Gómez','Vida','Hospitalización','Emergencia cardíaca',25000000,25000000,'Aprobada',3),
(9,'2026-05-01','Diana Carolina Pérez','Hogar','Incendio','Daño eléctrico por tormenta',2100000,NULL,'En proceso',NULL),
(10,'2026-05-05','Jorge Parrado','Vehicular','Choque','Daño menor en parqueadero',3500000,NULL,'En proceso',NULL);

-- Grants base para PUBLIC (UI puede leer)
GRANT USAGE ON DATABASE AI_SUMMIT TO ROLE PUBLIC;
GRANT USAGE ON SCHEMA AI_SUMMIT.PUBLIC TO ROLE PUBLIC;
GRANT SELECT ON ALL TABLES IN SCHEMA AI_SUMMIT.PUBLIC TO ROLE PUBLIC;

-- ---------------------------------------------------------------------
-- Confirmacion
-- ---------------------------------------------------------------------
SELECT '00_base.sql completado' AS status,
       'Siguiente: 01_streamlit.sql, 02_analyst_search.sql, 03_agent.sql' AS siguiente;
