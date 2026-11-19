# TPI DATA4QUALITY — ¿Qué se apaga si se cae una sola empresa?

Pipeline de datos para el TPI de Aspectos Avanzados de Calidad de Software (UTN FRRe).

## Qué hace cada archivo

| Paso | Archivo | Dónde se corre | Qué produce |
|---|---|---|---|
| 1 | `sql/01_dependencias_top_ar.sql` | Consola de BigQuery (navegador) | `data/dependencias_top_ar.csv`: sitios más usados desde Argentina + su CDN e infraestructura |
| 2 | `src/02_radar_argentina.py` | Tu compu | Tráfico de Argentina durante las caídas de Cloudflare, AWS y CrowdStrike + cortes registrados |
| 3 | `src/05_radar_ranking_ar.py` | Tu compu | Top 100 **ordenado** de dominios en Argentina (CrUX solo da tramos) |
| 4 | `src/03_etl_dependencias.py` | Tu compu | Limpieza + % de sitios por empresa + `dependencias.json` para la pieza + top 100 para revisar |
| 5 | `src/04_sitios_chaco.py` | Tu compu (opcional) | Lo mismo para sitios locales o del top 100 sin datos |

`src/comun.py` no se corre solo: tiene la tabla de empresas y las rutas que usan los demás.

## Seguridad: qué hace y qué no hace cada script

- **Ningún script escribe en sistemas ajenos.** Solo hacen consultas de lectura (GET) a la API pública de Cloudflare Radar y consultas DNS públicas, y guardan archivos en `data/`.
- `03` no usa internet: solo lee y escribe CSV/JSON.
- `04` hace lo mismo que el navegador al abrir un sitio (pregunta el DNS). No escanea puertos ni descarga páginas.
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
3. Pegá el contenido de `sql/01_dependencias_top_ar.sql`.
4. **Antes de ejecutar**, mirá el estimado de bytes arriba a la derecha.
5. Ejecutá → *Guardar resultados* → *CSV (archivo local)* → guardalo como `data/dependencias_top_ar.csv`.

No hace falta descargar HTTP Archive: la tabla completa pesa petabytes, pero BigQuery la procesa del lado de Google y vos te bajás solo el resultado (unos pocos MB).

### 2. Token de Cloudflare Radar
1. Creá una cuenta gratuita en Cloudflare.
2. *My Profile → API Tokens → Create Token → Custom token* con **un solo permiso: Radar → Read**. Nada más.
3. Copiá `.env.example` como `.env` y pegá el token ahí (el `.env` no se sube).

### 3. Radar
```powershell
python src/02_radar_argentina.py
```
```powershell
python src/05_radar_ranking_ar.py
```

### 4. ETL
```powershell
python src/03_etl_dependencias.py
```
Abrí `data/top100_revision.csv` y completá la columna `revisado_a_mano`.

### 5. (Opcional) Sitios de Chaco o del top 100 sin datos
Completá `data/sitios_chaco.csv` con los dominios reales (verificalos en el navegador):
```powershell
python src/04_sitios_chaco.py
```
```powershell
python src/04_sitios_chaco.py data/top100_sin_datos.csv
```

### Complemento manual para la perspectiva de Uso
Google Trends (https://trends.google.com), región Argentina, en las fechas de cada caída: búsquedas como "no anda", "caída", "Cloudflare", "WhatsApp no funciona". Se descarga como CSV desde la misma página. Muestra mejor que Radar qué vivió la gente.

## Transformaciones (para la ficha de evidencia)
1. Se toman los orígenes del tramo top 10.000 de CrUX para Argentina (octubre 2026).
2. Se cruzan con la home móvil de cada sitio en HTTP Archive (crawl del 1/10/2026). Los que no están se descartan y se informa el % de cobertura.
3. Cada proveedor detectado (CDN, tecnología) se traduce a su empresa madre con la tabla de `src/comun.py`.
4. Se separan dependencias **duras** (CDN, hosting, nube, proxy: si se caen, el sitio no carga) y **blandas** (login y pagos de terceros: falla una función).
5. La empresa principal de un sitio es la de su CDN; si no hay CDN, la primera dependencia dura conocida.
6. El rubro se asigna con patrones sobre el dominio (heurística, se revisa a mano en el top 100).
7. Radar: los valores son normalizados, no cantidades. Se compara cada serie contra su propia mediana (`valor_rel`) y contra la misma franja de la semana anterior.

## Licencias y citas
- **Chrome UX Report** — Google. Dataset público en BigQuery.
- **HTTP Archive** — dataset público en BigQuery; detección de tecnologías con Wappalyzer.
- **Cloudflare Radar** — datos de la API bajo CC BY-NC 4.0 (uso no comercial, citar la fuente).

## Limitaciones a declarar
- Mide **sitios web**, no apps móviles.
- CrUX solo cuenta usuarios de Chrome que comparten estadísticas, y su ranking es por tramos.
- El top 100 de Radar se basa en consultas DNS a 1.1.1.1: es otra población, por eso se usa solo para ordenar y revisar.
- HTTP Archive rastrea desde EE. UU. y analiza solo la home de cada sitio.
- La detección de CDN y tecnologías (Wappalyzer) no es perfecta.
- Cada sitio pesa lo mismo en los porcentajes, sea Google o un sitio chico (por eso se informa también el top 1.000 aparte).
- Que un sitio use una CDN no significa que se caiga entero si esa CDN cae: es una *dependencia*, no una certeza de caída. Los postmortems ayudan a calibrar esto.
- Radar mide tráfico que pasa por Cloudflare: durante una caída la gente reintenta, así que el tráfico puede no bajar.
