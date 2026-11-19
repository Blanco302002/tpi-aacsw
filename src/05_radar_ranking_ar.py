"""
05_radar_ranking_ar.py
Top 100 ORDENADO de dominios más usados desde Argentina, según Cloudflare
Radar (ranking basado en consultas a su DNS 1.1.1.1; licencia CC BY-NC 4.0).

Sirve para "revisar el top 100 a mano": CrUX solo da tramos (top 1000,
top 5000...), no puestos.

Qué hace: solo CONSULTA (GET) la API pública de Radar.

Uso:
    python src/05_radar_ranking_ar.py
Salida:
    data/radar_top100_ar.csv   (puesto, dominio, categorias)
Después corré 03_etl_dependencias.py: lo cruza solo.
"""

import csv
import importlib

from comun import DATOS

radar = importlib.import_module("02_radar_argentina")  # reusa token y llamada a la API


def main():
    DATOS.mkdir(exist_ok=True)
    res = radar.get("/ranking/top", {"location": radar.LOCATION, "limit": 100})
    lista = next((v for k, v in res.items() if k != "meta" and isinstance(v, list)), [])
    if not lista:
        raise SystemExit(f"La respuesta no trae ranking. Claves recibidas: {list(res)}")
    filas = [{
        "puesto": d.get("rank", i + 1),
        "dominio": d.get("domain"),
        "categorias": " | ".join(c.get("name", "") for c in d.get("categories") or []),
    } for i, d in enumerate(lista)]
    ruta = DATOS / "radar_top100_ar.csv"
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["puesto", "dominio", "categorias"])
        w.writeheader()
        w.writerows(filas)
    print(f"OK {ruta.name} ({len(filas)} dominios). Primeros 10:")
    for f in filas[:10]:
        print(f"  {f['puesto']:>3}. {f['dominio']}")


if __name__ == "__main__":
    main()
