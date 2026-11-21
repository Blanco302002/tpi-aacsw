# TPI DATA4QUALITY — ¿Qué se apaga si se cae una sola empresa?

Aspectos Avanzados de Calidad de Software · UTN FRRe · Entrega y pitch: 3/12/2026, 18 h, Aula 2.2
Estado al 18/11/2026: **datos recolectados y procesados.** Falta la pieza visual y el guion.

---

## 1. La situación (con esto abre el pitch, sin definiciones técnicas)
Martes 18 de noviembre de 2025, 10 de la mañana. En Argentina, ChatGPT, X y miles de sitios
muestran el mismo cartel: *"Por favor, desbloquee challenges.cloudflare.com para continuar"*.
Ese día, miles de personas buscaron en Google **"qué es cloudflare"**: una empresa de la que
nunca habían oído hablar y de la que dependía buena parte de lo que usan todos los días.

## 2. Los datos

| Fuente | Qué aporta | Período | Unidad de análisis | Acceso / licencia |
|---|---|---|---|---|
| Chrome UX Report (`country_summary`, AR) | Los ~10.000 sitios más usados desde Argentina | Octubre 2026 | Origen web | BigQuery, público |
| HTTP Archive (`crawl.pages`) | CDN, nube y servicios de cada sitio | Crawl 1/10/2026 | Home móvil del sitio | BigQuery, público |
| Cloudflare Radar API | Tráfico de Argentina en cada caída, top 100 ordenado, cortes registrados | 2024–2025 | Intervalos de 15 min | API gratuita, CC BY-NC 4.0 |
| Google Trends | Qué buscó la gente en cada caída | Mes de cada caída | Día | Público, descarga manual |
| Postmortems oficiales | Por qué se cayó cada servicio | — | Incidente | Blogs de Cloudflare, AWS y CrowdStrike |
| DNS + ASN (Team Cymru) | Sitios de Chaco y del top 100 fuera de HTTP Archive | Nov. 2026 | Dominio | Consultas públicas |

Repositorio con los scripts, los datos y el detalle de las transformaciones:
https://github.com/Blanco302002/tpi-aacsw (SQL + 6 scripts Python + README).

## 3. El descubrimiento

**Dependencia (Producto).** De 7.713 sitios con datos:
- El **56 %** depende de **Cloudflare**, el **27 %** de **Amazon (AWS)** y el **12 %** de **Google**.
- El **72 %** depende de al menos una de esas tres.
- Entre los 1.000 más usados la proporción se mantiene: 56 % Cloudflare y 32 % AWS.
- El 11 % no usa ningún intermediario detectable. Muchos son sitios del Estado y de Chaco (UTN FRRe,
  Nuevo Banco del Chaco, Gobierno del Chaco), alojados en proveedores locales.

**Lo que vivió la gente (Uso).** Tráfico web de Argentina contra la misma hora de la semana anterior:

| Caída | Hora en Argentina | Tráfico web (Radar) | Búsquedas en Google (Trends) |
|---|---|---|---|
| Cloudflare, 18/11/2025 | 8:20 a 14:06 | **−94 % a las 11:00** | De ~2 a 100 en un día |
| AWS, 20/10/2025 | 3:48 a 19:00 | −7 % (casi sin cambio) | De ~5 a 100 en un día |
| CrowdStrike, 19/07/2024 | desde la 1:09 | −5 % (casi sin cambio) | De 0 a 100 en un día |

- La caída de la empresa de la que **más** dependemos fue la única que **vació** la web argentina.
- Las otras dos se sintieron de otra forma: en apps, en computadoras de empresas y de madrugada. Igual
  la gente salió a buscar qué pasaba.
- En las tres, la gente aprendió el nombre de una empresa invisible **el día que falló**.

**Las apps que usamos todos los días (57 servicios conocidos en Argentina).** Lista curada de apps y
webs: bancos y billeteras, Estado, compras, transporte, viajes, redes, streaming, IA, estudio y trabajo, y medios.
Incluye servicios de Chaco (Nuevo Banco del Chaco, campus UTN FRRe). Detalle en `data/resultados/servicios.csv`.

| Empresa principal | Servicios | Ejemplos |
|---|---|---|
| Cloudflare | 20 | ChatGPT, Claude, X, Discord, Zoom, Uber, Galicia, Naranja X, Brubank, MODO, Mi Argentina, PedidosYa, Rappi, JetSMART, Flybondi, campus UTN FRRe, Clarín, TN |
| Amazon (AWS) | 9 | Mercado Pago, Mercado Libre, Mercado Play, Amazon, Netflix, Prime Video, Cabify, Slack, DeepSeek |
| Akamai | 7 | Santander, BBVA, TikTok, Disney+, HBO Max, Infobae, La Nación |
| Proveedor argentino | 6 | ARCA, SUBE, Cuenta DNI, Banco Macro, Flow, Nuevo Banco del Chaco |
| Meta (propia) | 3 | WhatsApp, Instagram, Facebook |
| Google | 4 | YouTube, Gemini, Google Meet, Aerolíneas Argentinas |
| Otras | 8 | Microsoft (Teams), Vercel (Ualá, Granola), Fastly (Spotify), Imperva (ANSES), propias (DiDi, Telegram), F5 (Banco Nación) |

Cruce entre la dependencia (DNS) y lo que se cayó (noticias):
- **Cloudflare (18/11/2025):** dependen 21 (en 20 es la principal). Se cayeron, confirmado o en medios, X, ChatGPT, Claude, Uber, Discord y Naranja X.
- **AWS (20/10/2025):** dependen 23 (en 9 es la principal). Se cayeron Mercado Pago, Mercado Libre, Ualá, Naranja X, Amazon, Prime Video, Netflix y Slack. Naranja X y Ualá lo confirmaron con un comunicado.
- **CrowdStrike (19/07/2024):** se cayeron **Aerolíneas Argentinas** y **JetSMART**, según fuentes de las empresas. Bloomberg Línea habló de un impacto "muy limitado" en Argentina. CrowdStrike no pasa por la web: rompió las **computadoras con Windows** de las empresas. Por eso el DNS dice que Aerolíneas depende de Google y aun así se cayó con CrowdStrike: es una dependencia que **ningún dato de la web puede ver**.
- **Un dato curioso:** en la caída de Cloudflare, los medios también nombraron 13 servicios que según el DNS **no dependen** de Cloudflare (Mercado Pago, bancos, WhatsApp). Puede ser ruido (la gente culpa a todo) o una dependencia oculta. El cartel que vio la gente, *"desbloquee challenges.cloudflare.com"*, es un control anti-bots de Cloudflare que otros sitios insertan, por ejemplo en un login, y el DNS no lo ve. Queda como hipótesis.

**Hipótesis puestas a prueba** (`sql/08_historial_y_global.sql`: HTTP Archive guarda la CDN de cada web mes a mes;
resultados en `data/resultados/historial_servicios.csv` y `comparacion_mundo.csv`):

1. **¿Los servicios nombrados en la caída de Cloudflare usaban Cloudflare en ese momento?** **No.** Mercado Pago y
   Mercado Libre (AWS), Santander (Akamai), WhatsApp e Instagram (Meta), Spotify (Fastly), Gemini (Google), ARCA y
   Banco Nación (sin CDN) tenían la misma infraestructura en noviembre de 2025 que hoy. Lo que queda es **ruido**
   (la gente culpa a todo, y su propia conexión también podía fallar) o **dependencias ocultas** (usar Cloudflare
   *por dentro*, como el control anti-bots en un login). No se puede distinguir con estos datos.
2. **¿Alguien se fue de Cloudflare después de la caída?** **Algunos sí, pero no hubo éxodo.**
   - Entre noviembre de 2025 y enero de 2026, **DeepSeek** pasó de Cloudflare a AWS. **X** pasó a Fastly y para
     octubre de 2026 **volvió a Cloudflare**. **SUBE** (recarga) dejó Cloudflare por Imperva durante 2026.
   - Al mismo tiempo, **Uber** (web móvil) y el **campus de la UTN FRRe** **se sumaron** a Cloudflare.
   - Dominios de los servicios que usan Cloudflare: 13 antes de la caída, 11 dos meses después y **13 de nuevo hoy**.
   - **Lectura:** la concentración se recuperó en menos de un año. Un mes de HTTP Archive es una foto: muestra
     que cambiaron, no **por qué**.
3. **¿Argentina depende de Cloudflare más que el mundo?** **No: igual o un poco menos.** Top 10.000:

   | Empresa | Argentina | Mundo |
   |---|---|---|
   | Cloudflare | 56 % | 60 % |
   | Amazon (AWS) | 27 % | 32 % |
   | Akamai | 3 % | 12 % |
   | Proveedores locales u otros | 13 % | 8 % |

   **No es un problema argentino: es la forma en que está armada internet.** Argentina usa menos Akamai y
   más proveedores locales que el promedio mundial.
4. **¿Y si se cae Akamai?** Akamai es la principal en 7 servicios (Santander, BBVA, TikTok, Disney+, HBO Max,
   Infobae, La Nación). **Precedente:** el 22/07/2021 una actualización de configuración de Akamai dejó sitios
   de clientes inaccesibles hasta una hora (ver `docs/postmortems.md`).

> **Aviso para mostrar en la pieza:** la infraestructura se consultó por DNS en noviembre de 2026, no el día de cada
> caída; un servicio pudo cambiar de proveedor en el medio. Además, el DNS ve la "puerta de entrada" de cada
> servicio, no lo que usa por dentro. Por eso "¿se cayó?" se apoya en noticias, no en el DNS.

**Por qué se cayó (Proceso).** Según los postmortems oficiales (resumen completo con fuentes y citas en
[`docs/postmortems.md`](postmortems.md)), ninguna fue un hackeo: fueron **cambios de rutina que el proceso dejó llegar a todos**.
- **Cloudflare:** un cambio de permisos en una base de datos hizo que un archivo de configuración generado automáticamente
  duplicara su tamaño. Ese archivo se copia solo a toda la red cada 5 minutos, y el software que lo lee tenía un límite
  fijo: el proxy se colgó en todo el mundo. Se cayó también **Turnstile**, el anti-bots que otros sitios insertan en su
  login, lo que refuerza la hipótesis de las **dependencias ocultas**.
- **AWS:** dos partes de un sistema **automático** de DNS se pisaron entre sí (una falla latente) y dejaron vacía la
  dirección de DynamoDB en us-east-1. Detrás cayeron en cadena otros servicios. Duró unas 14 horas y media.
- **CrowdStrike:** una actualización de contenido de rutina con un error no detectado llegó a **todas** las computadoras
  conectadas en 78 minutos, **sin despliegue por etapas**: 8,5 millones de equipos con Windows (menos del 1 %), que hubo
  que arreglar a mano. Su análisis de causa raíz concluye que esos contenidos deberían tener despliegue por etapas.
- **Los cuatro informes son "sin culpables"**: describen fallas del sistema, no de personas. Tres piden disculpas públicas.

## 4. Recién acá: el concepto de calidad
- **Producto → Fiabilidad** (ISO/IEC 25010:2023): disponibilidad, tolerancia a fallos, recuperabilidad.
  Muchos sitios distintos, un mismo punto único de falla.
- **Proceso:** despliegue gradual (*canary*), presupuesto de error y postmortems sin culpables
  (*Site Reliability Engineering*; *Software Engineering at Google*). Lo que habría frenado el
  cambio antes de llegar a todos.
- **Uso:** la calidad en uso la paga quien no eligió al proveedor ni sabía que existía.
- **Cierre:** *"El producto falló, la causa estaba en el proceso, y lo pagaron las personas"*
  (Principios de Calidad Total).

Contexto, no eje: DORA 2025, Stack Overflow Survey 2025, GitHub Innovation Graph.

## 5. Pieza visual (modalidad híbrida, a construir)
1. **Historia de apertura:** el cartel de error, el gráfico de tráfico del 18/11 que cae 94 % y las
   búsquedas de "qué es cloudflare".
2. **Explorador:** *"Marcá las apps que usás y elegí qué empresa se cae"*. La persona ve cuáles de
   *sus* apps se apagan y cuáles se cayeron de verdad. Usa `data/resultados/servicios.json` (57 servicios).

## 6. Limitaciones (detalle en el README)
- El ranking de ~7.700 mide sitios web; las apps solo están en la lista curada de 57 servicios.
- El DNS de los 57 servicios es de noviembre de 2026, no del día de cada caída, y ve solo la puerta de entrada.
- "Se cayó" sale de noticias: "no reportado" no significa que haya andado bien. CrUX solo cuenta usuarios de Chrome y ordena por tramos, no por puesto.
- El 21 % del top no está en HTTP Archive. La detección de tecnologías (Wappalyzer) no es perfecta.
- Depender de una empresa no garantiza caerse con ella: es una dependencia, no una certeza.
- Durante la caída de Cloudflare, el propio Radar marca que su medición estuvo afectada.
- Trends da valores relativos (0–100) dentro de cada búsqueda: no se comparan alturas entre caídas.
- Se excluyeron 271 sitios para adultos (2,7 %). Las apuestas online (~290 sitios) se mantienen como rubro.

## 7. Próximos pasos
| Fechas | Tarea |
|---|---|
| 21–23/11 | ~~Revisar a mano el top 100~~ (hecho: 60 de 100 eran técnicos → lista curada de 57 servicios). ~~Leer los 3 postmortems y anotar citas~~ (hecho: `docs/postmortems.md`). |
| 24–27/11 | Pieza visual: historia de apertura + explorador. |
| 28–29/11 | Ficha de evidencia. |
| 30/11–2/12 | Guion del pitch (8 min) y ensayos. |
| 3/12 | Presentación. |
