"""
07_servicios.py
¿De qué empresa depende cada uno de los 50 servicios (apps y webs) más
conocidos en Argentina? Y ¿se cayó en cada una de las tres caídas?

Para cada dominio del servicio pregunta al DNS público lo mismo que el
navegador o la app antes de conectarse: a qué nombre apunta (CNAME) y de qué
red (empresa) es la IP (Team Cymru). No escanea ni entra a ningún sistema.

Entrada:  data/fuentes/servicios_ar.csv   lista curada a mano (dominios + "¿se cayó?" con fuente)
          data/resultados/sitios_limpios.csv   (opcional) lo que vio HTTP Archive de la web
Salidas:  data/resultados/servicios.csv   50 filas, una por servicio
          data/resultados/servicios.json  lo mismo, para el explorador de la pieza

Uso:
    pip install dnspython
    python src/07_servicios.py
"""

import csv
import importlib
import json
from datetime import date

from comun import CSV_ENC, FUENTES, RESULTADOS, empresas_en

dns04 = importlib.import_module("04_sitios_chaco")  # reusa ips, cname_chain, asn_de
dns04.RES.lifetime = 10  # algunos DNS (bancos, universidades) tardan más de 5 s

ENTRADA = FUENTES / "servicios_ar.csv"
SITIOS_HA = RESULTADOS / "sitios_limpios.csv"
CAIDAS = ["cloudflare", "aws", "crowdstrike"]

AVISO = ("La infraestructura se consultó por DNS el {fecha}, no el día de cada caída: "
         "un servicio pudo cambiar de proveedor en el medio. Por eso la columna "
         "'¿se cayó?' se apoya en noticias y postmortems, no en el DNS. "
         "Además, el DNS muestra el servidor público de cada servicio, no su "
         "infraestructura interna.")


def empresa_de_red(red):
    """Empresa conocida, proveedor argentino o el nombre de la red tal cual."""
    if not red:
        return None
    conocidas = [e for e in empresas_en(red) if e != "Otra"]
    if conocidas:
        return conocidas[0]
    # Team Cymru: "AS7303 - Telecom Argentina S.A., AR" → país al final
    nombre = red.split(" - ", 1)[-1]
    nombre, _, pais = nombre.rpartition(",")
    if pais.strip() == "AR":
        return f"Proveedor argentino ({nombre.strip()})"
    return f"Propia u otra ({(nombre or red).strip()})"


def sitios_http_archive():
    if not SITIOS_HA.exists():
        return {}
    with open(SITIOS_HA, encoding="utf-8-sig") as f:
        return {r["host"]: r for r in csv.DictReader(f)}


def analizar_dominio(dominio, ha):
    lista_ips = []
    for _ in range(3):  # hasta 3 intentos: a veces el DNS no contesta a tiempo
        lista_ips = dns04.ips(dominio)
        if lista_ips:
            break
    cname = dns04.cname_chain(dominio)
    asn, red = dns04.asn_de(lista_ips[0]) if lista_ips else (None, None)
    empresas = []
    # 1) El CNAME suele delatar la CDN (ej. x.cdn.cloudflare.net, x.akamaiedge.net)
    empresas += [e for e in empresas_en(" ".join(cname)) if e != "Otra"]
    # 2) Lo que detectó HTTP Archive en la web (si el dominio está en el top de CrUX).
    #    Va antes que el dueño de la IP: ve la CDN aunque use IPs propias del servicio.
    if dominio in ha:
        empresas += [e for e in ha[dominio]["duras"].split(" | ") if e and e != "Otra"]
    # 3) Dueño de la red de la IP
    e_red = empresa_de_red(red)
    if e_red:
        empresas.append(e_red)
    return {
        "dominio": dominio,
        "responde": bool(lista_ips),
        "cname": " > ".join(cname),
        "red": red or "",
        "empresas": list(dict.fromkeys(empresas)),  # sin repetidos, en orden
    }


def main():
    hoy = date.today().isoformat()
    ha = sitios_http_archive()
    with open(ENTRADA, encoding="utf-8-sig") as f:
        servicios = list(csv.DictReader(f))

    filas, para_json = [], []
    for s in servicios:
        detalle = [analizar_dominio(d, ha) for d in s["dominios"].split()]
        empresas = list(dict.fromkeys(e for d in detalle for e in d["empresas"]))
        principal = empresas[0] if empresas else "sin respuesta del DNS"
        fila = {
            "servicio": s["servicio"], "rubro": s["rubro"], "tipo": s["tipo"],
            "alcance": s["alcance"],
            "empresa_principal": principal,
            "empresas_infra": " | ".join(empresas),
            **{f"afectado_{c}": s[f"afectado_{c}"] for c in CAIDAS},
            **{f"fuente_{c}": s[f"fuente_{c}"] for c in CAIDAS},
            "detalle_dns": " ; ".join(
                f"{d['dominio']}: {' > '.join(filter(None, [d['cname'], d['red']])) or 'sin respuesta'}"
                for d in detalle),
            "fecha_consulta_dns": hoy,
        }
        filas.append(fila)
        para_json.append({
            "servicio": s["servicio"], "rubro": s["rubro"], "tipo": s["tipo"],
            "alcance": s["alcance"], "principal": principal, "empresas": empresas,
            "se_cayo": {c: {"afectado": s[f"afectado_{c}"], "fuente": s[f"fuente_{c}"]}
                        for c in CAIDAS},
        })
        print(f"{s['servicio']:30} {principal}")

    try:
        with open(RESULTADOS / "servicios.csv", "w", newline="", encoding=CSV_ENC) as f:
            w = csv.DictWriter(f, fieldnames=filas[0].keys())
            w.writeheader()
            w.writerows(filas)
    except PermissionError:
        raise SystemExit("\nNo puedo guardar data/resultados/servicios.csv: cerralo en Excel y volvé a correr.")
    salida = {
        "metadatos": {
            "fuente": "Lista curada (data/fuentes/servicios_ar.csv) + DNS público + Team Cymru",
            "fecha_consulta_dns": hoy,
            "aviso": AVISO.format(fecha=hoy),
            "no_reportado": "'no reportado' significa que no se encontró una fuente que lo "
                            "confirme, no que el servicio haya funcionado bien.",
        },
        "servicios": para_json,
    }
    with open(RESULTADOS / "servicios.json", "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=1)
    print(f"\nOK data/resultados/servicios.csv y servicios.json ({len(filas)} servicios)")


if __name__ == "__main__":
    main()
