# TPI DATA4QUALITY — ¿Qué se apaga si se cae una sola empresa?

Pipeline de datos para el TPI de Aspectos Avanzados de Calidad de Software (UTN FRRe).
El resumen de hallazgos está en [`docs/informe_avance.md`](docs/informe_avance.md), y el de los postmortems (por qué se cayó cada uno) en [`docs/postmortems.md`](docs/postmortems.md).

## Dónde está cada cosa

```
sql/                         consultas de BigQuery (se corren en la consola web)
  sitios_top_ar.sql            sitios más usados desde Argentina + su CDN y nube
  historial_y_mundo.sql        CDN de cada servicio antes/después de las caídas + top mundial
src/
  comun.py                     rutas, token y tabla de empresas (lo usan todos)
  dependencias/                PRODUCTO: ¿de qué empresas dependemos?
    sitios_top.py                limpia BigQuery y calcula % de sitios por empresa
    servicios.py                 los 57 servicios conocidos: empresa (DNS) y si se cayeron (noticias)
    historial_y_mundo.py         ¿cambiaron de proveedor? ¿Argentina vs. el mundo?
    dns_sitios.py                consultas DNS (las usa servicios.py; sola: sitios de Chaco)
    radar_ranking.py             top 100 de dominios de Radar (referencia)
  caidas/                      PERSONA: ¿qué pasó en cada caída?
    radar_trafico.py             tráfico de Argentina en las 3 caídas (Cloudflare Radar)
    resumen_caidas.py            cuánto cayó el tráfico en cada una
  explorador/
    datos_explorador.py          incrusta los datos en explorador/index.html
data/
  fuentes/                     lo que se bajó o se armó a mano, tal cual
  resultados/                  lo que generan los scripts
explorador/index.html          la página del QR (bilingüe)
docs/                          informe de avance y postmortems (PROCESO: ¿por qué se cayó?)
```

**Los dos archivos más importantes:**
- `data/resultados/servicios.csv` (y `.json`): **57 servicios conocidos en Argentina** (apps y webs), de qué empresa depende cada uno y si se cayó en cada caída.
- `data/resultados/dependencias.json`: los ~7.700 sitios más usados desde Argentina y su empresa.

**Hechos a mano:** Google Trends (`data/fuentes/trends/`, ver su `LEEME.md`) y la revisión del top 100 de Radar
(`data/fuentes/top100_revision_manual.csv`: 60 de 100 son dominios técnicos).

## El explorador para el celular: `explorador/index.html`
Página **bilingüe** (castellano por defecto, inglés con `?lang=en` o con el botón EN), un solo archivo que abre sin
internet. Es para que el público la abra desde el **QR** de la presentación.
1. **Publicarlo en Vercel:** en vercel.com → *Add New → Project* → importá el repo `tpi-aacsw` →
   **Root Directory: `explorador`** → Framework: *Other* → *Deploy*. Te da una URL `https://….vercel.app`.
2. **Dos QR (castellano e inglés):** se arman **una sola vez**, después del deploy, con un script local que no está
   en el repo (`presentacion/qr_explorador.py`). Apuntan a `URL?lang=es` y `URL?lang=en`.

## Presentación y pieza HTML (solo locales, no están en el repo)
La presentación en inglés (`presentacion/`, PowerPoint + memes) y la primera versión HTML (`pieza/`) quedan solo
en la compu del presentador: están en `.gitignore`. `src/explorador/datos_explorador.py` las actualiza si existen.

## Seguridad: qué hace y qué no hace cada script

- **Ningún script escribe en sistemas ajenos.** Solo hacen consultas de lectura (GET) a la API pública de Cloudflare Radar y consultas DNS públicas, y guardan archivos en `data/`.
- `sitios_top.py`, `resumen_caidas.py`, `historial_y_mundo.py` y `datos_explorador.py` no usan internet: solo leen y escriben CSV/JSON.
- `dns_sitios.py` y `servicios.py` hacen lo mismo que el navegador al abrir un sitio (preguntan el DNS). No escanean puertos ni descargan páginas.
- El token de Cloudflare se lee del archivo `.env`, que está en `.gitignore` y **no se sube** al repo.
- Dependencias: solo `pandas`, `requests` y `dnspython` (paquetes muy usados, de PyPI).

## Cómo correrlo

### 0. Instalar (una vez)
```powershell
pip install -r requirements.txt
```

### 1. BigQuery (15 min, en el navegador)
1. Entrá a https://console.cloud.google.com/bigquery con tu cuenta de Google.
2. Creá un proyecto (ej. `tpi-data4quality`). El *sandbox* es gratis y no pide tarjeta: si una consulta superara el límite, falla, no cobra.
3. Pegá el contenido de `sql/sitios_top_ar.sql`.
4. **Antes de ejecutar**, mirá el estimado de bytes arriba a la derecha.
5. Ejecutá → *Guardar resultados* → *CSV (archivo local)* → guardalo como `data/fuentes/dependencias_top_ar.csv`.

No hace falta descargar HTTP Archive: la tabla completa pesa petabytes, pero BigQuery la procesa del lado de Google y vos te bajás solo el resultado (unos pocos MB).

### 2. Token de Cloudflare Radar
1. Creá una cuenta gratuita en Cloudflare.
2. *My Profile → API Tokens → Create Token → Custom token* con **un solo permiso: Radar → Read**. Nada más.
3. Copiá `.env.example` como `.env` y pegá el token ahí (el `.env` no se sube).

### 3. Scripts, en orden
```powershell
python src/caidas/radar_trafico.py
```
```powershell
python src/dependencias/sitios_top.py
```
```powershell
python src/caidas/resumen_caidas.py
```
```powershell
python src/dependencias/servicios.py
```
```powershell
python src/explorador/datos_explorador.py
```
Opcionales: `src/dependencias/dns_sitios.py` (sitios de Chaco) y `src/dependencias/radar_ranking.py` (top 100 de Radar).

### 4. Historial y comparación con el mundo
1. En BigQuery, corré `sql/historial_y_mundo.sql` (mirá el estimado: unos 400 GB, entra en el TB gratis).
2. Guardá el resultado como `data/fuentes/historial_global.csv`.
3. Corré:
```powershell
python src/dependencias/historial_y_mundo.py
```

### Para sumar o sacar servicios
Editá `data/fuentes/servicios_ar.csv` (una fila por servicio, dominios separados por espacio) y volvé a correr `src/dependencias/servicios.py` y `src/explorador/datos_explorador.py`.
Si querés que el historial incluya los nuevos dominios, hay que regenerar la lista de `sql/historial_y_mundo.sql`.
Las columnas `afectado_<caída>` van con una fuente (link) en `fuente_<caída>`.

## Transformaciones (para la ficha de evidencia)
1. Se toman los orígenes del tramo top 10.000 de CrUX para Argentina (octubre 2026).
2. Se cruzan con la home móvil de cada sitio en HTTP Archive (crawl del 1/10/2026). Los que no están se descartan y se informa el % de cobertura.
3. Cada proveedor detectado (CDN, tecnología) se traduce a su empresa madre con la tabla de `src/comun.py`.
4. Se separan dependencias **duras** (CDN, hosting, nube, proxy: si se caen, el sitio no carga) y **blandas** (login y pagos de terceros: falla una función).
5. La empresa principal de un sitio es la de su CDN; si no hay CDN, la primera dependencia dura conocida.
6. El rubro se asigna con patrones sobre el dominio (heurística).
7. Radar: los valores son normalizados entre 0 y 1 dentro de cada serie, no cantidades. Se pide una sola serie continua desde una semana antes del evento, y cada momento se compara con la misma hora de la semana anterior (`dif_pct`). Pedir evento y control como dos series separadas da escalas distintas: se probó y se descartó.
8. Ventanas de cada caída (en `src/caidas/resumen_caidas.py`): horarios de inicio y fin según cada postmortem.
9. **Los 57 servicios** (`fuentes/servicios_ar.csv`) son una lista curada: conocidos en Argentina, mezcla de apps y webs, nacionales, globales y locales (Chaco, provincia de Buenos Aires). Se armó así porque el top 100 de Radar resultó mayormente técnico (revisión a mano: 60 de 100).
10. Para cada servicio, la empresa se obtiene en este orden: el CNAME del dominio (delata la CDN), lo que detectó HTTP Archive (si la web está en el top) y el dueño de la red de la IP (Team Cymru). La empresa principal es la primera del primer dominio.
11. "¿Se cayó?" sale de noticias y postmortems, con tres valores: **confirmado** (comunicado de la empresa o error observado por el medio), **reportado en medios** (listas de notas, a menudo basadas en quejas de usuarios) y **no reportado**.

## Licencias y citas
- **Chrome UX Report** — Google. Dataset público en BigQuery.
- **HTTP Archive** — dataset público en BigQuery; detección de tecnologías con Wappalyzer.
- **Cloudflare Radar** — datos de la API bajo CC BY-NC 4.0 (uso no comercial, citar la fuente).
- **Team Cymru** — servicio público de IP → ASN por DNS.
- Las noticias usadas para "¿se cayó?" están linkeadas fila por fila en `servicios_ar.csv`.

## Limitaciones a declarar
- **El DNS de los 50 servicios se consultó hoy (ver `fecha_consulta_dns`), no el día de cada caída.** Un servicio pudo cambiar de proveedor en el medio. Por eso "¿se cayó?" se apoya en noticias y postmortems, no en el DNS.
- El DNS muestra el servidor **público** de cada servicio (su "puerta de entrada"), no su infraestructura interna: una app puede depender de otras empresas por dentro (login, anti-bots, pagos) sin que se vea.
- "No reportado" significa que no se encontró una fuente, no que el servicio haya andado bien.
- Algunas dependencias no se ven en ningún dato de la web: CrowdStrike rompió computadoras con Windows de las empresas (por ejemplo Aerolíneas Argentinas), no sus sitios.
- Servicios nombrados en una caída sin depender de esa empresa: el historial (`historial_y_mundo`) descartó que hubieran cambiado de proveedor (en noviembre de 2025 tenían la misma infraestructura que hoy). Quedan dos explicaciones que estos datos no distinguen: ruido de reportes o dependencias ocultas.
- HTTP Archive toma una foto por mes: muestra **que** un servicio cambió de proveedor, no **por qué**.
- Las listas de "afectados" de los medios mezclan fallas reales con quejas de usuarios: hay servicios reportados en la caída de Cloudflare que, según el DNS, no dependen de Cloudflare.
- Los sitios del top 10.000 son **webs**; las apps solo están en la lista de 50 servicios.
- CrUX solo cuenta usuarios de Chrome que comparten estadísticas, y su ranking es por tramos.
- HTTP Archive rastrea desde EE. UU. y analiza solo la home de cada sitio. La detección de tecnologías (Wappalyzer) no es perfecta.
- Cada sitio pesa lo mismo en los porcentajes, sea Google o un sitio chico (por eso se informa también el top 1.000 aparte).
- Que un sitio use una CDN no significa que se caiga entero si esa CDN cae: es una *dependencia*, no una certeza de caída.
- Radar mide tráfico que pasa por Cloudflare: durante una caída la gente reintenta, así que el tráfico puede no bajar.
- En la caída de Cloudflare, el propio Radar marca que su medición estuvo afectada entre 11:48 y 14:42 UTC (`fuentes/radar_anotaciones.csv`). La baja del 94 % mezcla tráfico que no llegó y tráfico que no se pudo registrar.
- Se excluyeron del análisis los sitios para adultos (cantidad en `dependencias.json → metadatos`).
