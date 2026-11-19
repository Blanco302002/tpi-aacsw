-- =====================================================================
-- 01_dependencias_top_ar.sql
-- ¿De qué empresas de infraestructura dependen los sitios más usados
-- desde Argentina?
--
-- Fuentes (públicas, gratuitas en BigQuery):
--   * Chrome UX Report (CrUX): sitios más visitados por país.
--   * HTTP Archive: CDN y tecnologías detectadas en cada sitio (Wappalyzer).
--
-- Dónde correrlo: consola de BigQuery (console.cloud.google.com/bigquery).
-- El "BigQuery sandbox" alcanza: 1 TB de consultas por mes, sin tarjeta.
-- En el sandbox no te pueden cobrar: si te pasás del TB, la consulta falla.
--
-- ANTES DE CORRER: mirá arriba a la derecha cuántos bytes va a procesar.
-- Lo esperable es del orden de decenas a pocos cientos de GB.
-- El resultado (lo que descargás) son unos pocos MB.
--
-- OJO con "rank": en CrUX no es un puesto (1, 2, 3...) sino un tramo
-- (1000 = está entre los 1000 primeros, 5000 = entre el 1001 y el 5000...).
-- Para un top 100 ordenado usá src/05_radar_ranking_ar.py.
-- =====================================================================

DECLARE mes   INT64 DEFAULT 202610;        -- último mes publicado de CrUX (AAAAMM)
DECLARE crawl DATE  DEFAULT '2026-10-01';  -- crawl de HTTP Archive del mismo mes
DECLARE top_n INT64 DEFAULT 10000;         -- 1000, 5000, 10000, 50000...

WITH top_ar AS (
  SELECT origin, MIN(rank) AS rank_ar
  FROM `chrome-ux-report.materialized.country_summary`
  WHERE yyyymm = mes
    AND country_code = 'ar'
    AND rank <= top_n
  GROUP BY origin
),

ha AS (
  -- Lo que HTTP Archive detectó en la home de cada sitio (versión móvil).
  SELECT
    page,
    JSON_VALUE(summary, '$.cdn') AS cdn,
    ARRAY(
      SELECT AS STRUCT
        t.technology AS tecnologia,
        c            AS categoria,
        -- dura: si se cae, el sitio no carga.
        -- blanda: si se cae, falla una función (login, pago).
        IF(c IN ('Authentication', 'Payment processors'), 'blanda', 'dura') AS tipo
      FROM UNNEST(technologies) AS t, UNNEST(t.categories) AS c
      WHERE c IN ('CDN', 'PaaS', 'IaaS', 'Hosting', 'Reverse proxies',
                  'Authentication', 'Payment processors')
    ) AS infra
  FROM `httparchive.crawl.pages`
  WHERE date = crawl
    AND client = 'mobile'
    AND is_root_page
)

SELECT
  t.origin,
  t.rank_ar,
  ha.page IS NOT NULL     AS en_http_archive,  -- cobertura: declararla en la ficha
  ha.cdn,
  TO_JSON_STRING(ha.infra) AS infra_json
FROM top_ar AS t
LEFT JOIN ha
  ON ha.page = CONCAT(t.origin, '/')
ORDER BY t.rank_ar, t.origin;

-- Guardar: "Guardar resultados" → "CSV (archivo local)"
-- con el nombre data/dependencias_top_ar.csv
-- (el archivo local tiene límite de 10 MB: con top_n = 10000 sobra).
--
-- Si falla por el mes, probá con el anterior (202609 y '2026-09-01').
-- Si `httparchive.crawl.pages` da error de tabla, probá con
-- `httparchive.all.pages` (esquema anterior, mismas columnas).
