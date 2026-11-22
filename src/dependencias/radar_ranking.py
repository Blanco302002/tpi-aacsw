"""
radar_ranking.py
Top 100 ORDENADO de dominios más usados desde Argentina, según Cloudflare
Radar (ranking basado en consultas a su DNS 1.1.1.1; licencia CC BY-NC 4.0).

Sirve para "revisar el top 100 a mano": CrUX solo da tramos (top 1000,
top 5000...), no puestos.

Qué hace: solo CONSULTA (GET) la API pública de Radar.

Uso:
    python src/dependencias/radar_ranking.py
Salida:
    data/fuentes/radar_top100_ar.csv   (puesto, dominio, categorias)
Se usa como referencia para los dominios de las apps (ver servicios_ar.csv).
"""

import csv

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # src/: para importar comun y los otros temas

from comun import CSV_ENC, FUENTES

from caidas import radar_trafico as radar  # reusa token y llamada a la API


def main():
    res = radar.get("/ranking/top", {"location": radar.LOCATION, "limit": 100})
    lista = next((v for k, v in res.items() if k != "meta" and isinstance(v, list)), [])
    if not lista:
        raise SystemExit(f"La respuesta no trae ranking. Claves recibidas: {list(res)}")
    filas = [{
        "puesto": d.get("rank", i + 1),
        "dominio": d.get("domain"),
        "categorias": " | ".join(c.get("name", "") for c in d.get("categories") or []),
    } for i, d in enumerate(lista)]
    ruta = FUENTES / "radar_top100_ar.csv"
    with open(ruta, "w", newline="", encoding=CSV_ENC) as f:
        w = csv.DictWriter(f, fieldnames=["puesto", "dominio", "categorias"])
        w.writeheader()
        w.writerows(filas)
    print(f"OK {ruta.name} ({len(filas)} dominios). Primeros 10:")
    for f in filas[:10]:
        print(f"  {f['puesto']:>3}. {f['dominio']}")


if __name__ == "__main__":
    main()
