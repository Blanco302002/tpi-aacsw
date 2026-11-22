"""
09_datos_pieza.py
Junta los datos que usa la pieza visual y los incrusta en pieza/index.html,
así la pieza abre sin internet y sin servidor. No usa internet.

Si se vuelven a correr los scripts 02–08, correr este al final para que la
pieza muestre los números nuevos.

Entrada:  data/resultados/*  y  data/fuentes/*
Salida:   pieza/index.html   (reemplaza lo que está entre DATOS:INICIO y DATOS:FIN)

Uso:
    python src/09_datos_pieza.py
"""

import csv
import json
import re
from datetime import datetime, timedelta

from comun import FUENTES, RAIZ, RESULTADOS

PIEZA = RAIZ / "pieza" / "index.html"
INICIO, FIN = "<!-- DATOS:INICIO -->", "<!-- DATOS:FIN -->"


def leer_csv(ruta):
    with open(ruta, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def trends():
    """Serie diaria de Google Trends (las 2 primeras líneas son encabezado de Google)."""
    with open(FUENTES / "trends" / "cloudflare_serie_AR.csv", encoding="utf-8-sig") as f:
        lineas = f.read().splitlines()
    filas = list(csv.reader(lineas[2:]))[1:]
    serie = [{"d": d, "v": int(v)} for d, v, *_ in filas if d]
    alza = [r["query"] for r in leer_csv(FUENTES / "trends" / "cloudflare_busquedas_en_alza_AR.csv")]
    elegidas = ["que es cloudflare", "por favor, desbloquee challenges.cloudflare.com para continuar.",
                "chatgpt cloudflare", "cloudflare buenos aires", "se cayo cloudflare", "cloudflare error 500"]
    return {"serie": serie, "busquedas": [q for q in elegidas if q in alza]}


def radar():
    """Tráfico web (HTTP) del 18/11/2025 en hora argentina, contra la semana anterior."""
    filas = leer_csv(FUENTES / "radar_cloudflare_2025-11-18.csv")
    desde = datetime(2025, 11, 18, 3, 0)   # 00:00 en Argentina
    hasta = desde + timedelta(hours=24)
    serie = []
    for r in filas:
        if r["fuente"] != "http":
            continue
        t = datetime.strptime(r["timestamp_utc"], "%Y-%m-%dT%H:%M:%SZ")
        if desde <= t <= hasta:
            serie.append({"h": round((t - desde).total_seconds() / 3600, 2),
                          "v": float(r["valor"]),
                          "c": float(r["valor_semana_anterior"]) if r["valor_semana_anterior"] else None,
                          "d": float(r["dif_pct"]) if r["dif_pct"] else None})
    return serie


def resumen_caidas():
    return [{k: r[k] for k in ("evento", "fuente", "inicio_ar", "fin_ar", "dif_pct_promedio_caida",
                               "dif_pct_peor_momento", "peor_momento_ar")}
            for r in leer_csv(RESULTADOS / "resumen_caidas.csv")]


def empresas():
    filas = leer_csv(RESULTADOS / "resumen_por_empresa.csv")
    return [{"empresa": r["empresa"], "pct": float(r["pct_dura"]),
             "pct1000": float(r["pct_dura_top1000"])} for r in filas]


def mundo():
    return [{"empresa": r["empresa"], "ar": float(r["pct_argentina"]), "mundo": float(r["pct_mundo"])}
            for r in leer_csv(RESULTADOS / "comparacion_mundo.csv")]


def main():
    dep = json.load(open(RESULTADOS / "dependencias.json", encoding="utf-8"))
    serv = json.load(open(RESULTADOS / "servicios.json", encoding="utf-8"))
    datos = {
        "generado": datetime.now().strftime("%Y-%m-%d"),
        "trends": trends(),
        "radar": radar(),
        "caidas": resumen_caidas(),
        "empresas": empresas(),
        "sitios": {"con_datos": dep["metadatos"]["sitios_con_datos"],
                   "en_top": dep["metadatos"]["sitios_en_top"],
                   "excluidos": dep["metadatos"].get("excluidos_por_rubro", {})},
        "concentracion": dep["concentracion"],
        "mundo": mundo(),
        "servicios": serv["servicios"],
        "aviso_dns": serv["metadatos"]["aviso"],
    }
    bloque = f"{INICIO}\n<script>window.DATOS = {json.dumps(datos, ensure_ascii=False)};</script>\n{FIN}"
    patron = re.compile(re.escape(INICIO) + r".*?" + re.escape(FIN), re.S)
    # Páginas HTML que llevan los datos adentro (abren sin internet)
    for pagina in (PIEZA, RAIZ / "explorador" / "index.html"):
        if not pagina.exists():
            continue
        html = pagina.read_text(encoding="utf-8")
        if not patron.search(html):
            raise SystemExit(f"No encuentro los marcadores {INICIO} / {FIN} en {pagina}")
        pagina.write_text(patron.sub(lambda _: bloque, html), encoding="utf-8")
        print(f"OK {pagina.relative_to(RAIZ)} actualizada")
    # Datos para el PowerPoint (presentacion/generar_pptx.js)
    (RAIZ / "presentacion").mkdir(exist_ok=True)
    with open(RAIZ / "presentacion" / "datos.json", "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False)
    print(f"OK presentacion/datos.json ({len(bloque) // 1024} KB, "
          f"{len(datos['servicios'])} servicios, {len(datos['radar'])} puntos de Radar)")


if __name__ == "__main__":
    main()
