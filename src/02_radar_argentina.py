"""
02_radar_argentina.py
Tráfico de internet en Argentina durante las grandes caídas, según
Cloudflare Radar (API gratuita, datos bajo licencia CC BY-NC 4.0).

Qué hace: solo CONSULTA (GET) la API pública de Radar. No escribe nada en
tu cuenta de Cloudflare ni toca ningún otro sistema.

Uso:
    1. Poné tu token en el archivo .env (ver README) o en la terminal.
    2. python src/02_radar_argentina.py

Genera:
    data/radar_<evento>.csv     serie de tráfico (15 min) del evento + semana anterior
    data/radar_outages_ar.csv   cortes de internet registrados en Argentina

Cómo leer los valores: Radar NO da cantidad de pedidos, da valores
normalizados entre 0 y 1 (MIN0_MAX) dentro de cada serie. Por eso se pide
UNA sola serie continua que va desde una semana antes hasta el final del
evento: así el evento y su control comparten la misma escala, y se compara
cada momento con la misma hora del mismo día de la semana anterior
("dif_pct": -50 = la mitad del tráfico habitual).
(Probado: pedir evento y control como dos series separadas da escalas
distintas y no se pueden comparar.)

Nota: Radar mide el tráfico que pasa por Cloudflare. Durante una caída, la
gente sigue pidiendo páginas (y recibe errores), así que el tráfico puede
no bajar. Hay que mirar los datos antes de usarlos en la pieza.
"""

import csv
import os
from datetime import datetime, timedelta, timezone

import requests

from comun import DATOS, cargar_env

API = "https://api.cloudflare.com/client/v4/radar"
LOCATION = "AR"

# Ventanas en UTC (Argentina = UTC-3), con margen de un día antes y después.
# Inicio aproximado de cada caída según su postmortem:
#   Cloudflare 18/11/2025 ~11:20 UTC | AWS 20/10/2025 ~06:50 UTC | CrowdStrike 19/07/2024 ~04:10 UTC
EVENTOS = {
    "cloudflare_2025-11-18":  ("2025-11-17T12:00:00Z", "2025-11-19T12:00:00Z"),
    "aws_2025-10-20":         ("2025-10-19T12:00:00Z", "2025-10-21T12:00:00Z"),
    "crowdstrike_2024-07-19": ("2024-07-18T12:00:00Z", "2024-07-20T12:00:00Z"),
}

# Desde cuándo buscar cortes registrados (cubre las tres caídas).
OUTAGES_DESDE = "2024-07-01T00:00:00Z"


class ErrorRadar(Exception):
    pass


def token():
    cargar_env()
    t = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not t:
        raise SystemExit("Falta CLOUDFLARE_API_TOKEN: crealo en el archivo .env (ver README).")
    return t


def get(path, params):
    r = requests.get(
        f"{API}{path}",
        headers={"Authorization": f"Bearer {token()}"},
        params={**params, "format": "JSON"},
        timeout=60,
    )
    try:
        body = r.json()
    except ValueError:
        raise ErrorRadar(f"HTTP {r.status_code}, respuesta no es JSON")
    if r.status_code != 200 or not body.get("success", False):
        raise ErrorRadar(f"HTTP {r.status_code}: {body.get('errors')}")
    return body["result"]


def una_semana_antes(iso):
    d = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ") - timedelta(days=7)
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


def serie_continua(path, inicio, fin):
    """Una sola serie desde una semana antes del inicio hasta el fin."""
    for intervalo in ("15m", "1h"):  # si 15 min no está disponible, por hora
        try:
            res = get(path, {"location": LOCATION, "aggInterval": intervalo,
                             "dateStart": una_semana_antes(inicio), "dateEnd": fin})
            break
        except ErrorRadar:
            if intervalo == "1h":
                raise
    s = res["serie_0"]
    anotaciones = ((res.get("meta") or {}).get("confidenceInfo") or {}).get("annotations") or []
    return dict(zip(s["timestamps"], s["values"])), anotaciones


def guardar_evento(nombre, inicio, fin):
    filas, notas = [], []
    for fuente, path in [("http", "/http/timeseries"), ("netflows", "/netflows/timeseries")]:
        valores, anotaciones = serie_continua(path, inicio, fin)
        for ts in sorted(valores):
            if ts < inicio:
                continue  # la semana anterior solo se usa como control
            v, vc = valores[ts], valores.get(una_semana_antes(ts))
            dif = (float(v) / float(vc) - 1) * 100 if v is not None and vc else None
            filas.append({"fuente": fuente, "timestamp_utc": ts, "valor": v,
                          "valor_semana_anterior": vc,
                          "dif_pct": round(dif, 1) if dif is not None else None})
        for a in anotaciones:
            notas.append({"evento": nombre, "fuente": fuente,
                          "inicio": a.get("startDate"), "fin": a.get("endDate"),
                          "tipo": a.get("eventType"), "descripcion": a.get("description"),
                          "link": a.get("linkedUrl")})
    ruta = DATOS / f"radar_{nombre}.csv"
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=filas[0].keys())
        w.writeheader()
        w.writerows(filas)
    print(f"OK {ruta.name} ({len(filas)} filas, {len(notas)} anotaciones de Radar)")
    return notas


def guardar_outages():
    hasta = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    anotaciones, offset = [], 0
    while True:  # paginado: la API devuelve de a 'limit'
        res = get("/annotations/outages", {
            "location": LOCATION, "dateStart": OUTAGES_DESDE, "dateEnd": hasta,
            "limit": 100, "offset": offset,
        })
        lote = res.get("annotations", [])
        anotaciones += lote
        if len(lote) < 100:
            break
        offset += 100
    filas = [{
        "inicio": a.get("startDate"), "fin": a.get("endDate"),
        "causa": (a.get("outage") or {}).get("outageCause"),
        "tipo": (a.get("outage") or {}).get("outageType"),
        "alcance": a.get("scope"), "descripcion": a.get("description"),
        "link": a.get("linkedUrl"),
    } for a in anotaciones]
    ruta = DATOS / "radar_outages_ar.csv"
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["inicio", "fin", "causa", "tipo",
                                          "alcance", "descripcion", "link"])
        w.writeheader()
        w.writerows(filas)
    print(f"OK {ruta.name} ({len(filas)} cortes desde {OUTAGES_DESDE[:10]})")


if __name__ == "__main__":
    DATOS.mkdir(exist_ok=True)
    token()  # si falta el token, cortar acá con un mensaje claro
    fallas, notas = 0, []
    for nombre, (ini, fin) in EVENTOS.items():
        try:
            notas += guardar_evento(nombre, ini, fin)
        except (ErrorRadar, requests.RequestException) as e:
            fallas += 1
            print(f"FALLÓ {nombre}: {e}")  # una ventana fallida no frena las demás
    # Anotaciones que Radar pega a cada serie (ej. "su propia medición estuvo afectada")
    with open(DATOS / "radar_anotaciones.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["evento", "fuente", "inicio", "fin",
                                          "tipo", "descripcion", "link"])
        w.writeheader()
        w.writerows(notas)
    try:
        guardar_outages()
    except (ErrorRadar, requests.RequestException) as e:
        fallas += 1
        print(f"FALLÓ outages: {e}")
    if fallas:
        print(f"\n{fallas} consulta(s) fallaron. Revisá el mensaje de error de cada una.")
