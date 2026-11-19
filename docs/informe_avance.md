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
https://github.com/Blanco302002/tpi-aacsw (SQL + 5 scripts Python + README).

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

**Por qué se cayó (Proceso).** En los tres casos un cambio llegó a todo el mundo al mismo tiempo:
- **Cloudflare:** un archivo de configuración generado automáticamente duplicó su tamaño y se distribuyó a toda la red.
- **AWS:** un error en la automatización de DNS de un servicio interno, en una sola región, de la que dependían muchas otras cosas.
- **CrowdStrike:** una actualización de contenido enviada a todas las computadoras a la vez, sin despliegue gradual.

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
2. **Explorador:** *"Marcá los sitios que usás y elegí qué empresa se cae"*. La persona ve cuáles de
   *sus* sitios se apagan. Usa `data/dependencias.json`.

## 6. Limitaciones (detalle en el README)
- Mide sitios web, no apps. CrUX solo cuenta usuarios de Chrome y ordena por tramos, no por puesto.
- El 21 % del top no está en HTTP Archive. La detección de tecnologías (Wappalyzer) no es perfecta.
- Depender de una empresa no garantiza caerse con ella: es una dependencia, no una certeza.
- Durante la caída de Cloudflare, el propio Radar marca que su medición estuvo afectada.
- Trends da valores relativos (0–100) dentro de cada búsqueda: no se comparan alturas entre caídas.
- Se excluyeron 271 sitios para adultos (2,7 %). Las apuestas online (~290 sitios) se mantienen como rubro.

## 7. Próximos pasos
| Fechas | Tarea |
|---|---|
| 21–23/11 | Revisar a mano el top 100 (`data/top100_revision.csv`). Leer los 3 postmortems y anotar citas. |
| 24–27/11 | Pieza visual: historia de apertura + explorador. |
| 28–29/11 | Ficha de evidencia. |
| 30/11–2/12 | Guion del pitch (8 min) y ensayos. |
| 3/12 | Presentación. |
