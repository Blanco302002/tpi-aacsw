"""
03_etl_dependencias.py
Limpia el CSV de BigQuery y calcula de qué empresa depende cada sitio.

Solo lee y escribe archivos dentro de data/. No usa internet.

Entrada:  data/fuentes/dependencias_top_ar.csv     (resultado de sql/01_dependencias_top_ar.sql)
Salidas:  data/resultados/sitios_limpios.csv       una fila por sitio, con empresas y rubro
          data/resultados/resumen_por_empresa.csv  % de sitios que dependen de cada empresa
          data/resultados/dependencias.json        datos de los ~7.700 sitios para la pieza

Dos tipos de dependencia:
    dura    CDN, hosting, nube, proxy. Si se cae, el sitio no carga.
    blanda  login y pagos de terceros. Si se cae, falla una función.

Uso:
    python src/03_etl_dependencias.py
"""

import json
import re
import sys
from datetime import date

import pandas as pd

from comun import CSV_ENC, EMPRESAS, FUENTES, RESULTADOS, empresas_en

ENTRADA = FUENTES / "dependencias_top_ar.csv"
CATEGORIAS_BLANDAS = {"Authentication", "Payment processors"}
# Rubros que se sacan del análisis (se informa cuántos en los metadatos).
# "Apuestas" se deja: es uso real y es parte de la historia en Argentina.
EXCLUIR_RUBROS = {"Adultos"}
ORDEN = {e: i for i, (_, e) in enumerate(EMPRESAS)}


# --- 1. Empresas de cada sitio -------------------------------------------
def ordenar(empresas):
    """Sin repetidos, en el orden de la tabla EMPRESAS ("Otra" al final)."""
    return sorted(set(empresas), key=lambda e: ORDEN.get(e, len(ORDEN)))


def sin_otra_si_hay_conocida(empresas):
    return [e for e in empresas if e != "Otra"] or empresas


def dependencias(fila):
    """Devuelve (empresa del CDN, empresas duras, empresas blandas)."""
    del_cdn = empresas_en(fila.get("cdn"))
    duras, blandas = list(del_cdn), []
    try:
        items = json.loads(fila.get("infra_json") or "[]") or []
    except (json.JSONDecodeError, TypeError):
        items = []
    for item in items:
        tipo = item.get("tipo") or (
            "blanda" if item.get("categoria") in CATEGORIAS_BLANDAS else "dura")
        destino = blandas if tipo == "blanda" else duras
        destino += empresas_en(item.get("tecnologia"))
    duras = sin_otra_si_hay_conocida(ordenar(duras))
    blandas = sin_otra_si_hay_conocida(ordenar(blandas))
    # La principal es la del CDN (por donde entra todo el tráfico);
    # si no se detectó CDN, la primera dependencia dura conocida.
    principal = next((e for e in del_cdn if e != "Otra"), None) \
        or next((e for e in duras if e != "Otra"), None) \
        or ("Otra" if duras else "Sin CDN detectado")
    return principal, duras, blandas


# --- 2. Rubro del sitio (heurística por dominio: declararla en la ficha) ---
# Los patrones van anclados al comienzo de una parte del dominio:
# "(^|\.)x\." encuentra x.com pero no dropbox.com.
RUBROS = [
    # Primero adultos y apuestas, para que una quiniela .gov.ar quede en Apuestas.
    (r"xvideos|xnxx|porn|xhamster|(^|[^a-z])sex|sexo|escort|onlyfans|hentai|xxx"
     r"|redtube|youporn|brazzers|chaturbate|stripchat|bongacams|spankbang|eporner"
     r"|tnaflix|rule34|erome|fapello|simpcity|cumlouder|poringa|camsoda|cam4|nsfw"
     r"|milf|nude|desnud",                                                      "Adultos"),
    (r"(?<!alfa)(?<!alpha)bet(?!ter|a\.|a-|a$)|casino|apuesta|ganamos|ganaencasa"
     r"|1win|xbet|bplay|slot|poker|loteria|quiniela|codere|ruleta|bingo"
     r"|tragamoneda|jackpot|jugadon|lotto",                                     "Apuestas"),
    (r"\.gob\.ar$|\.gov\.ar$|(^|\.)(afip|arca|anses)\.",                        "Estado"),
    (r"\.edu\.ar$|\.edu$|(^|\.)(utn|uba|unne|moodle|campus)\.",                "Educación"),
    (r"banco|(^|\.)(bbva|galicia|santander|macro|nbch|brubank|uala|mercadopago"
     r"|naranjax|modo|personalpay)\.",                                          "Bancos y pagos"),
    (r"(^|\.)(mercadolibre|tiendanube|fravega|garbarino|musimundo|pedidosya"
     r"|rappi|temu|shein|amazon)\.",                                            "Compras y delivery"),
    (r"(^|\.)(clarin|lanacion|infobae|pagina12|tn|ole|perfil|ambito|cronica"
     r"|eldiarioar)\.",                                                         "Medios"),
    (r"(^|\.)(netflix|spotify|youtube|twitch|disneyplus|disney|max|hbomax"
     r"|primevideo|flow)\.",                                                    "Entretenimiento"),
    (r"(^|\.)(whatsapp|instagram|facebook|tiktok|x|twitter|telegram|threads"
     r"|linkedin)\.",                                                           "Redes y mensajería"),
    (r"(^|\.)(google|bing|yahoo|duckduckgo|wikipedia)\.",                      "Buscadores y consulta"),
]


def host_de(origin):
    return re.sub(r"^https?://", "", str(origin)).split("/")[0].lower()


def rubro_de(host):
    for patron, rubro in RUBROS:
        if re.search(patron, host):
            return rubro
    return "Otros"


def tramo_de(rank):
    return "Top 1.000" if rank <= 1000 else f"Top {int(rank):,}".replace(",", ".")


# --- 3. Resúmenes ---------------------------------------------------------
def pct_por_empresa(df, columna, total):
    s = (df.explode(columna).dropna(subset=[columna])
         .groupby(columna)["origin"].nunique())
    return (s.div(total).mul(100).round(1).rename("pct").reset_index()
            .rename(columns={columna: "empresa"}))


def a_bool(serie):
    return serie.astype(str).str.strip().str.lower().isin({"true", "1", "verdadero"})


def main():
    if not ENTRADA.exists():
        sys.exit(f"No encuentro {ENTRADA}. Corré primero la consulta de BigQuery (ver README).")

    df = pd.read_csv(ENTRADA)
    df["en_http_archive"] = a_bool(df["en_http_archive"])
    rubro_previo = df["origin"].apply(host_de).apply(rubro_de)
    excluidos = rubro_previo[rubro_previo.isin(EXCLUIR_RUBROS)].value_counts().to_dict()
    df = df[~rubro_previo.isin(EXCLUIR_RUBROS)].copy()
    print(f"Excluidos por rubro: {excluidos}")
    total_top = len(df)
    print(f"Sitios en el top de Argentina: {total_top}")
    print(f"Con datos en HTTP Archive:     {df['en_http_archive'].sum()} "
          f"({df['en_http_archive'].mean():.0%})")

    df = df[df["en_http_archive"]].copy()
    df[["empresa_principal", "duras", "blandas"]] = df.apply(
        lambda f: pd.Series(dependencias(f)), axis=1)
    df["host"] = df["origin"].apply(host_de)
    df["rubro"] = df["host"].apply(rubro_de)
    df["tramo"] = df["rank_ar"].apply(tramo_de)

    salida_sitios = df[["origin", "host", "rank_ar", "tramo", "rubro", "cdn",
                        "empresa_principal", "duras", "blandas"]].copy()
    for c in ("duras", "blandas"):
        salida_sitios[c] = salida_sitios[c].apply(" | ".join)
    salida_sitios.to_csv(RESULTADOS / "sitios_limpios.csv", index=False, encoding=CSV_ENC)

    # % de sitios que dependen de cada empresa, por tipo y por tramo
    n = len(df)
    top1k = df[df["rank_ar"] <= 1000]
    resumen = (pct_por_empresa(df, "duras", n).rename(columns={"pct": "pct_dura"})
               .merge(pct_por_empresa(df, "blandas", n).rename(columns={"pct": "pct_blanda"}),
                      on="empresa", how="outer")
               .merge(pct_por_empresa(top1k, "duras", max(len(top1k), 1))
                      .rename(columns={"pct": "pct_dura_top1000"}),
                      on="empresa", how="left")
               .fillna(0)
               .sort_values("pct_dura", ascending=False))
    resumen.to_csv(RESULTADOS / "resumen_por_empresa.csv", index=False, encoding=CSV_ENC)
    print(f"\n% de sitios que dependen de cada empresa (sobre {n} con datos):")
    print(resumen.head(12).to_string(index=False))

    sin_cdn = (df["empresa_principal"] == "Sin CDN detectado").mean() * 100
    print(f"\nSin CDN ni infraestructura detectada: {sin_cdn:.0f}%")

    # Concentración: ¿cuántas empresas (conocidas) explican la mayoría?
    conocidas = resumen[~resumen["empresa"].isin(["Otra"])]
    top3 = list(conocidas["empresa"].head(3))
    pct_top3 = df["duras"].apply(lambda l: bool(set(top3) & set(l))).mean() * 100
    print(f"Sitios que dependen (dura) de al menos una de {top3}: {pct_top3:.0f}%")


    # JSON para la pieza interactiva (incluye lo que pide la consigna:
    # procedencia, período, unidad de análisis, transformaciones, limitaciones)
    salida = {
        "metadatos": {
            "fuentes": ["Chrome UX Report (Google), country_summary, país AR",
                        "HTTP Archive, crawl.pages, cliente mobile, solo la home"],
            "periodo": "CrUX 2026-10 / HTTP Archive crawl 2026-10-01 (ver sql/01)",
            "unidad_de_analisis": "origen web (ej. https://www.ejemplo.com.ar)",
            "sitios_en_top": int(total_top),
            "excluidos_por_rubro": {k: int(v) for k, v in excluidos.items()},
            "sitios_con_datos": int(n),
            "transformaciones": "ver README, sección Transformaciones",
            "generado": date.today().isoformat(),
        },
        "concentracion": {"empresas": top3, "pct_sitios": round(pct_top3, 1),
                          "pct_sin_cdn": round(sin_cdn, 1)},
        "resumen": resumen.to_dict(orient="records"),
        "sitios": [
            {"dominio": f.host, "tramo": f.tramo, "rubro": f.rubro,
             "principal": f.empresa_principal, "duras": f.duras, "blandas": f.blandas}
            for f in df.itertuples()
        ],
    }
    with open(RESULTADOS / "dependencias.json", "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=1)
    print("\nOK sitios_limpios.csv, resumen_por_empresa.csv, dependencias.json")



if __name__ == "__main__":
    main()
