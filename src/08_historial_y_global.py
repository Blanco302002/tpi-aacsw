"""
08_historial_y_global.py
Analiza el resultado de sql/08_historial_y_global.sql. No usa internet.

A) ¿Algún servicio cambió de proveedor después de una caída?
   Para cada dominio de los servicios, la empresa principal según HTTP Archive
   en 5 momentos (antes de cada caída y después).
B) ¿Argentina depende de Cloudflare (y del resto) más o menos que el mundo?
   Mismo cálculo que el ETL (03), pero sobre el top 10.000 mundial.

Entrada:  data/fuentes/historial_global.csv   (bajado de BigQuery)
          data/fuentes/servicios_ar.csv
          data/resultados/resumen_por_empresa.csv   (el % de Argentina, del 03)
Salidas:  data/resultados/historial_servicios.csv   un dominio por fila, una columna por fecha
          data/resultados/comparacion_mundo.csv     % por empresa: Argentina vs. mundo

Uso:
    python src/08_historial_y_global.py
"""

import csv
import importlib
import sys

import pandas as pd

from comun import CSV_ENC, FUENTES, RESULTADOS

etl = importlib.import_module("03_etl_dependencias")  # mismas reglas que para Argentina

ENTRADA = FUENTES / "historial_global.csv"
FECHAS = {
    "2024-07-01": "antes CrowdStrike",
    "2025-10-01": "antes AWS",
    "2025-11-01": "antes Cloudflare",
    "2026-01-01": "después Cloudflare",
    "2026-10-01": "hoy",
}


def principal(fila):
    p, _, _ = etl.dependencias(fila)
    return p


def historial(df):
    servicios = list(csv.DictReader(open(FUENTES / "servicios_ar.csv", encoding="utf-8-sig")))
    dominio_a_servicio = {d: s["servicio"] for s in servicios for d in s["dominios"].split()}
    s = df[df["es_servicio"]].copy()
    s["dominio"] = s["page"].str.replace(r"^https://|/$", "", regex=True)
    s["servicio"] = s["dominio"].map(dominio_a_servicio)
    s["principal"] = s.apply(principal, axis=1)
    tabla = (s.pivot_table(index=["servicio", "dominio"], columns="date",
                           values="principal", aggfunc="first")
             .reindex(columns=list(FECHAS)).fillna("sin dato"))
    tabla.columns = [f"{c} ({FECHAS[c]})" for c in tabla.columns]
    con_dato = tabla.apply(lambda r: {v for v in r if v != "sin dato"}, axis=1)
    tabla["cambio_de_proveedor"] = con_dato.apply(lambda v: "sí" if len(v) > 1 else "no")
    tabla = tabla.reset_index()
    tabla.to_csv(RESULTADOS / "historial_servicios.csv", index=False, encoding=CSV_ENC)
    cambios = tabla[tabla["cambio_de_proveedor"] == "sí"]
    print(f"A) {len(tabla)} dominios con datos en HTTP Archive; "
          f"{len(cambios)} cambiaron de empresa principal entre fechas:")
    print(cambios.drop(columns="cambio_de_proveedor").to_string(index=False) if len(cambios)
          else "   ninguno")
    return tabla


def comparacion(df):
    m = df[(df["date"] == "2026-10-01") & (df["rank"] <= 10000)].copy()
    m["origin"] = m["page"].str.rstrip("/")
    m["host"] = m["origin"].apply(etl.host_de)
    m = m[~m["host"].apply(etl.rubro_de).isin(etl.EXCLUIR_RUBROS)]
    m[["empresa_principal", "duras", "blandas"]] = m.apply(
        lambda f: pd.Series(etl.dependencias(f)), axis=1)
    mundo = etl.pct_por_empresa(m, "duras", len(m)).rename(columns={"pct": "pct_mundo"})
    ar = pd.read_csv(RESULTADOS / "resumen_por_empresa.csv", encoding="utf-8-sig")[
        ["empresa", "pct_dura"]].rename(columns={"pct_dura": "pct_argentina"})
    comp = ar.merge(mundo, on="empresa", how="outer").fillna(0)
    comp["diferencia_pp"] = (comp["pct_argentina"] - comp["pct_mundo"]).round(1)
    comp = comp.sort_values("pct_argentina", ascending=False)
    comp.to_csv(RESULTADOS / "comparacion_mundo.csv", index=False, encoding=CSV_ENC)
    print(f"\nB) Top 10.000 mundial ({len(m)} sitios con datos) vs. Argentina, "
          f"% de sitios que dependen de cada empresa:")
    print(comp.head(10).to_string(index=False))


def main():
    if not ENTRADA.exists():
        sys.exit(f"No encuentro {ENTRADA}. Corré sql/08_historial_y_global.sql en BigQuery (ver README).")
    df = pd.read_csv(ENTRADA)
    df["date"] = df["date"].astype(str).str[:10]
    df["es_servicio"] = etl.a_bool(df["es_servicio"])
    historial(df)
    comparacion(df)
    print("\nOK data/resultados/historial_servicios.csv y comparacion_mundo.csv")


if __name__ == "__main__":
    main()
