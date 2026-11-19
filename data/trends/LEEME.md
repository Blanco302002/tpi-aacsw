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

## Pendiente: serie temporal (lo más importante)
Bajar el gráfico **"Interés a lo largo del tiempo"** con un rango de **un mes** (un dato por día:
el pico se ve en el día de la caída) y con "downdetector" como término común a las tres caídas:

- Cloudflare: https://trends.google.com/trends/explore?date=2025-11-01%202025-11-30&geo=AR&q=cloudflare,downdetector
- AWS: https://trends.google.com/trends/explore?date=2025-10-01%202025-10-31&geo=AR&q=aws,downdetector
- CrowdStrike: https://trends.google.com/trends/explore?date=2024-07-01%202024-07-31&geo=AR&q=crowdstrike,downdetector

Guardarlos como `cloudflare_serie_AR.csv`, `aws_serie_AR.csv` y `crowdstrike_serie_AR.csv`.
