"""
04_sitios_chaco.py  (OPCIONAL)
Para sitios que no aparecen en los datos de HTTP Archive: sitios locales
(Moodle de la facultad, ATP, SAMEEP...) o los del top 100 que quedaron
"SIN DATOS".

Hace lo mismo que tu navegador al entrar a un sitio: pregunta el DNS y
averigua a qué red (empresa) pertenece la IP, usando el servicio público
de Team Cymru (también por DNS). No escanea puertos, no entra a ningún
sistema y no descarga páginas.

Uso:
    pip install dnspython
    python src/04_sitios_chaco.py                           # usa data/sitios_chaco.csv
    python src/04_sitios_chaco.py data/top100_sin_datos.csv # u otro CSV

Entrada: CSV con columnas dominio,nombre,rubro
Salida:  data/<nombre_entrada>_resultado.csv
"""

import csv
import sys
from pathlib import Path

import dns.resolver

from comun import DATOS, empresas_en

RES = dns.resolver.Resolver()
RES.lifetime = 5

# Sufijos públicos: si llegamos acá, el dominio no existe y no seguimos subiendo
# (si no, devolveríamos los DNS de "gob.ar", que no son del sitio).
SUFIJOS = {"ar", "com", "org", "net", "edu", "gov",
           "com.ar", "gob.ar", "gov.ar", "edu.ar", "org.ar", "net.ar", "int.ar", "mil.ar"}


def cname_chain(dominio):
    """Sigue los CNAME (ej. www.x.com -> x.cdn.cloudflare.net)."""
    cadena, actual = [], dominio
    for _ in range(8):
        try:
            r = RES.resolve(actual, "CNAME")
            actual = str(r[0].target).rstrip(".")
            cadena.append(actual)
        except Exception:
            break
    return cadena


def ips(dominio):
    try:
        return [str(r) for r in RES.resolve(dominio, "A")]
    except Exception:
        return []


def asn_de(ip):
    """Team Cymru: número de red (ASN) y su dueño, vía DNS público."""
    try:
        inv = ".".join(reversed(ip.split(".")))
        txt = str(RES.resolve(f"{inv}.origin.asn.cymru.com", "TXT")[0]).strip('"')
        asn = txt.split("|")[0].strip().split()[0]
        nombre = str(RES.resolve(f"AS{asn}.asn.cymru.com", "TXT")[0]).strip('"')
        return asn, nombre.split("|")[-1].strip()
    except Exception:
        return None, None


def nameservers(dominio):
    partes = dominio.split(".")
    for i in range(len(partes) - 1):
        candidato = ".".join(partes[i:])
        if candidato in SUFIJOS:
            break
        try:
            return [str(r).rstrip(".") for r in RES.resolve(candidato, "NS")]
        except Exception:
            continue
    return []


def main():
    entrada = Path(sys.argv[1]) if len(sys.argv) > 1 else DATOS / "sitios_chaco.csv"
    with open(entrada, encoding="utf-8") as f:
        sitios = [s for s in csv.DictReader(f) if (s.get("dominio") or "").strip()]
    if not sitios:
        sys.exit(f"{entrada} no tiene dominios.")

    filas = []
    for s in sitios:
        d = s["dominio"].strip().lower()
        lista_ips = ips(d)
        asn, red = asn_de(lista_ips[0]) if lista_ips else (None, None)
        cname = " > ".join(cname_chain(d))
        dns_ = " ".join(nameservers(d))
        # Misma tabla de empresas que el ETL, para poder comparar con el top nacional.
        hosting = [e for e in empresas_en(f"{cname} {red or ''}") if e != "Otra"]
        filas.append({
            **s,
            "cname": cname,
            "ip": lista_ips[0] if lista_ips else "",
            "asn": asn or "", "red": red or "",
            "dns": dns_,
            "empresa_hosting": " | ".join(hosting) or ("Otra" if red else "sin respuesta"),
            "empresa_dns": " | ".join(e for e in empresas_en(dns_) if e != "Otra") or "Otra",
        })
        print(f"{d:35} {filas[-1]['empresa_hosting']:22} ({red or 'sin respuesta'})")

    salida = DATOS / f"{entrada.stem}_resultado.csv"
    with open(salida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=filas[0].keys())
        w.writeheader()
        w.writerows(filas)
    print(f"\nOK {salida}")


if __name__ == "__main__":
    main()
