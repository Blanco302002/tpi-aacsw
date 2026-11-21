-- =====================================================================
-- 08_historial_y_global.sql
-- Dos preguntas en UNA sola consulta (para gastar menos cuota):
--
--  A) ¿Los servicios cambiaron de proveedor después de las caídas?
--     CDN e infraestructura de la web de cada uno de los 57 servicios
--     (data/fuentes/servicios_ar.csv) en 5 momentos:
--       2024-07-01  antes de CrowdStrike (19/07/2024)
--       2025-10-01  antes de AWS (20/10/2025)
--       2025-11-01  antes de Cloudflare (18/11/2025)
--       2026-01-01  dos meses después de Cloudflare
--       2026-10-01  el dato más nuevo (el mismo mes que el resto del TPI)
--
--  B) ¿Argentina depende de Cloudflare más o menos que el mundo?
--     Los 10.000 sitios más usados del MUNDO (rank global de HTTP Archive)
--     en 2026-10-01, para comparar con el 56 % de Argentina.
--
-- Esperable: ~5 veces la consulta 01 (unos 400 GB). Entra en el TB gratis
-- del sandbox. MIRÁ EL ESTIMADO ANTES DE EJECUTAR.
--
-- Guardar: "Guardar resultados" → "CSV (archivo local)" →
-- data/fuentes/historial_global.csv
--
-- Archivo generado a partir de servicios_ar.csv (si sumás servicios,
-- pedile a quien mantiene el repo que lo regenere).
-- =====================================================================

DECLARE servicios ARRAY<STRING> DEFAULT [
    'https://api.anthropic.com/',
    'https://api.deepseek.com/',
    'https://api.mercadopago.com/',
    'https://api.openai.com/',
    'https://api.x.com/',
    'https://app.slack.com/',
    'https://auth.afip.gob.ar/',
    'https://cabify.com/',
    'https://cdn.discordapp.com/',
    'https://chat.deepseek.com/',
    'https://chatgpt.com/',
    'https://claude.ai/',
    'https://discord.com/',
    'https://flybondi.com/',
    'https://frre.cvg.utn.edu.ar/',
    'https://frre.utn.edu.ar/',
    'https://g.whatsapp.net/',
    'https://gateway.discord.gg/',
    'https://gemini.google.com/',
    'https://granola.ai/',
    'https://graph.facebook.com/',
    'https://http2.mlstatic.com/',
    'https://i.instagram.com/',
    'https://i.scdn.co/',
    'https://i.ytimg.com/',
    'https://jetsmart.com/',
    'https://m.media-amazon.com/',
    'https://m.uber.com/',
    'https://meet.google.com/',
    'https://mi.argentina.gob.ar/',
    'https://open.spotify.com/',
    'https://pbs.twimg.com/',
    'https://play.hbomax.com/',
    'https://play.mercadolibre.com.ar/',
    'https://scontent.cdninstagram.com/',
    'https://slack.com/',
    'https://spclient.wg.spotify.com/',
    'https://static.xx.fbcdn.net/',
    'https://tarjetasube.sube.gob.ar/',
    'https://teams.microsoft.com/',
    'https://telegram.org/',
    'https://tn.com.ar/',
    'https://us05web.zoom.us/',
    'https://web.didiglobal.com/',
    'https://web.flow.com.ar/',
    'https://web.telegram.org/',
    'https://web.whatsapp.com/',
    'https://www.aerolineas.com.ar/',
    'https://www.amazon.com/',
    'https://www.anses.gob.ar/',
    'https://www.arca.gob.ar/',
    'https://www.argentina.gob.ar/',
    'https://www.bancogalicia.com.ar/',
    'https://www.bancoprovincia.com.ar/',
    'https://www.bbva.com.ar/',
    'https://www.bna.com.ar/',
    'https://www.brubank.com/',
    'https://www.clarin.com/',
    'https://www.didiglobal.com/',
    'https://www.disneyplus.com/',
    'https://www.facebook.com/',
    'https://www.flow.com.ar/',
    'https://www.galicia.ar/',
    'https://www.granola.ai/',
    'https://www.hbomax.com/',
    'https://www.infobae.com/',
    'https://www.instagram.com/',
    'https://www.lanacion.com.ar/',
    'https://www.macro.com.ar/',
    'https://www.mercadolibre.com.ar/',
    'https://www.mercadopago.com.ar/',
    'https://www.modo.com.ar/',
    'https://www.naranjax.com/',
    'https://www.nbch.com.ar/',
    'https://www.netflix.com/',
    'https://www.ole.com.ar/',
    'https://www.pedidosya.com.ar/',
    'https://www.primevideo.com/',
    'https://www.rappi.com.ar/',
    'https://www.santander.com.ar/',
    'https://www.sube.gob.ar/',
    'https://www.temu.com/',
    'https://www.tiktok.com/',
    'https://www.uala.com.ar/',
    'https://www.uber.com/',
    'https://www.youtube.com/',
    'https://x.com/',
    'https://youtubei.googleapis.com/',
    'https://zoom.us/'
  ];

SELECT
  date,
  page,
  rank,
  page IN UNNEST(servicios) AS es_servicio,
  JSON_VALUE(summary, '$.cdn') AS cdn,
  TO_JSON_STRING(ARRAY(
    SELECT AS STRUCT
      t.technology AS tecnologia,
      c            AS categoria,
      IF(c IN ('Authentication', 'Payment processors'), 'blanda', 'dura') AS tipo
    FROM UNNEST(technologies) AS t, UNNEST(t.categories) AS c
    WHERE c IN ('CDN', 'PaaS', 'IaaS', 'Hosting', 'Reverse proxies',
                'Authentication', 'Payment processors')
  )) AS infra_json
FROM `httparchive.crawl.pages`
WHERE date IN ('2024-07-01', '2025-10-01', '2025-11-01', '2026-01-01', '2026-10-01')
  AND client = 'mobile'
  AND is_root_page
  AND (
    page IN UNNEST(servicios)
    OR (date = '2026-10-01' AND rank <= 10000)
  )
ORDER BY es_servicio DESC, page, date;
