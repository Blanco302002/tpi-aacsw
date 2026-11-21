# Google Trends — qué hay en cada archivo

Fuente: Google Trends (https://trends.google.com), descargado a mano el 18/11/2026.
Los valores van de 0 a 100 y son **relativos dentro de cada búsqueda**: no son cantidades
y no se comparan entre archivos distintos.

| Archivo | Términos comparados | Región | Rango | Para qué sirve |
|---|---|---|---|---|
| `cloudflare_regiones_AR.csv` | Cloudflare, no anda, ChatGPT, se cayó | Argentina, por provincia | 17/11/2025 → 18/11/2026 | Poco: "ChatGPT" tapa a los demás términos. |
| `cloudflare_busquedas_en_alza_AR.csv` | Consultas relacionadas con "Cloudflare" | Argentina | 17/11/2025 → 18/11/2026 | **Mucho (perspectiva de Uso).** La gente buscó el mensaje de error que veía ("por favor, desbloquee challenges.cloudflare.com para continuar"), "que es cloudflare", "cloudflare buenos aires", "chatgpt cloudflare". |
| `cloudflare_busquedas_top_AR.csv` | Ídem, ordenadas por volumen | Argentina | Ídem | Casi igual al anterior. |
| `crowdstrike_regiones_AR.csv` | CrowdStrike, Pantalla azul de la muerte, windows, Microsoft | Argentina, por provincia | 01/07/2024 → 18/11/2026 | No sirve para el pico: "windows" tapa todo y el rango es de más de 2 años. |
| `crowdstrike_regiones_mundo.csv` | Ídem | Mundo, por país | Ídem | Ídem. "Pantalla azul" pesa más en Japón y el sudeste asiático. |
| `crowdstrike_busquedas_en_alza_mundo.csv` | Consultas relacionadas con "windows" | Mundo | Ídem | Muestra "windows crowdstrike" (+2.950 %) y "windows outage" (+3.200 %). |
| `crowdstrike_busquedas_top_mundo.csv` | Ídem, por volumen | Mundo | Ídem | Contexto. |

## Series temporales (un dato por día, un mes alrededor de cada caída)
Gráfico "Interés a lo largo del tiempo", Argentina, términos `<empresa>` y `downdetector`.
Ojo al leerlas: las 2 primeras líneas del CSV son encabezado de Google.

| Archivo | Rango | Día de la caída | Un día normal | Día siguiente |
|---|---|---|---|---|
| `cloudflare_serie_AR.csv` | 01/11 → 30/11/2025 | **100** (18/11) | 1–2 | 16 |
| `aws_serie_AR.csv` | 01/10 → 31/10/2025 | **100** (20/10) | 0–7 | 29 |
| `crowdstrike_serie_AR.csv` | 01/07 → 31/07/2024 | **100** (19/07) | 0 | 20 |

**Lectura:** en las tres caídas la gente en Argentina salió a buscar el nombre de una empresa
que un día normal casi nadie busca. Cloudflare pasó de ~2 a 100 (unas 50 veces más).
No se comparan las alturas entre archivos: cada uno tiene su propio 100.

Links usados:
- https://trends.google.com/trends/explore?date=2025-11-01%202025-11-30&geo=AR&q=cloudflare,downdetector
- https://trends.google.com/trends/explore?date=2025-10-01%202025-10-31&geo=AR&q=aws,downdetector
- https://trends.google.com/trends/explore?date=2024-07-01%202024-07-31&geo=AR&q=crowdstrike,downdetector
