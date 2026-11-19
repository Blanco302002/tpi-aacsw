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
normalizados. Por eso cada serie se pide junto con su semana de control en
la misma llamada, y además se agrega "valor_rel" = valor / mediana de su
propia serie (1.0 = un momento típico; 0.7 = 30 % menos que lo típico).
Comparar "valor_rel" del evento contra el de la semana anterior es válido
aunque la escala original fuera distinta.

Nota: Radar mide el tráfico que pasa por Cloudflare. Durante una caída, la
gente sigue pidiendo páginas (y recibe errores), así que el tráfico puede
no bajar. Hay que mirar los datos antes de usarlos en la pieza.
"""

import csv
import os
import statistics
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


def series_de(resultado):
    """Las series de la respuesta, en orden (serie_0/serie_1 o por nombre)."""
    return [v for k, v in resultado.items()
            if k != "meta" and isinstance(v, dict) and "timestamps" in v]


def relativo(valores):
    nums = [float(v) for v in valores if v is not None]
    mediana = statistics.median(nums) if nums else 0
    return [round(float(v) / mediana, 4) if mediana and v is not None else None
            for v in valores]


def guardar_evento(nombre, inicio, fin):
    filas = []
    for fuente, path in [("http", "/http/timeseries"), ("netflows", "/netflows/timeseries")]:
        # Evento y control en la misma llamada: misma normalización.
        res = get(path, {
            "location": LOCATION,
            "aggInterval": "15m",
            "name": ["evento", "control"],
            "dateStart": [inicio, una_semana_antes(inicio)],
            "dateEnd": [fin, una_semana_antes(fin)],
        })
        series = series_de(res)
        if len(series) < 2:
            raise ErrorRadar(f"{fuente}: se esperaban 2 series y llegaron {len(series)}")
        ev, ctl = series[0], series[1]
        ev_rel, ctl_rel = relativo(ev["values"]), relativo(ctl["values"])
        for i, ts in enumerate(ev["timestamps"]):
            filas.append({
                "fuente": fuente,
                "timestamp_utc": ts,
                "valor": ev["values"][i],
                "valor_semana_anterior": ctl["values"][i] if i < len(ctl["values"]) else None,
                "valor_rel": ev_rel[i],
                "valor_rel_semana_anterior": ctl_rel[i] if i < len(ctl_rel) else None,
            })
    ruta = DATOS / f"radar_{nombre}.csv"
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=filas[0].keys())
        w.writeheader()
        w.writerows(filas)
    print(f"OK {ruta.name} ({len(filas)} filas)")


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
    fallas = 0
    for nombre, (ini, fin) in EVENTOS.items():
        try:
            guardar_evento(nombre, ini, fin)
        except (ErrorRadar, requests.RequestException) as e:
            fallas += 1
            print(f"FALLÓ {nombre}: {e}")  # una ventana fallida no frena las demás
    try:
        guardar_outages()
    except (ErrorRadar, requests.RequestException) as e:
        fallas += 1
        print(f"FALLÓ outages: {e}")
    if fallas:
        print(f"\n{fallas} consulta(s) fallaron. Revisá el mensaje de error de cada una.")
