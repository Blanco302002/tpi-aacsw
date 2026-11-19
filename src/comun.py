"""
comun.py
Cosas que comparten los scripts: rutas, lectura del token y la tabla
que traduce "lo que se detectó" a "empresa dueña de la infraestructura".

No se corre solo: lo importan los demás scripts.
"""

import os
import re
import sys
from pathlib import Path

# La consola de Windows a veces no acepta tildes ni flechas: que no se rompa.
for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# Rutas absolutas: los scripts andan aunque los corras desde otra carpeta.
RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "data"


def cargar_env():
    """Lee el archivo .env de la raíz (si existe) y carga sus variables.

    Formato: una línea por variable, CLAVE=valor. El .env está en
    .gitignore, así que el token nunca se sube al repositorio.
    Una variable que ya esté definida en la terminal tiene prioridad.
    """
    ruta = RAIZ / ".env"
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


# --- Empresa "madre" de cada proveedor -----------------------------------
# Patrón (minúsculas) que aparece en el CDN, la tecnología, el CNAME,
# el dueño de la red (ASN) o los servidores DNS.
EMPRESAS = [
    (r"cloudflare",                                  "Cloudflare"),
    (r"amazon|\baws\b|cloudfront|awsdns",            "Amazon (AWS)"),
    (r"google|firebase|\bgcp\b|googlehosted",        "Google"),
    (r"akamai|edgekey|edgesuite",                    "Akamai"),
    (r"fastly",                                      "Fastly"),
    (r"azure|microsoft|msedge",                      "Microsoft (Azure)"),
    (r"vercel",                                      "Vercel"),
    (r"netlify",                                     "Netlify"),
    (r"imperva|incapsula",                           "Imperva"),
    (r"edgecast|edgio|verizon",                      "Edgio"),
    (r"bunny",                                       "Bunny"),
    (r"oracle",                                      "Oracle"),
]


def empresas_en(texto):
    """Todas las empresas conocidas que aparecen en el texto.

    Devuelve [] si el texto está vacío y ["Otra"] si hay un proveedor
    pero no es ninguno de la lista.
    """
    if not isinstance(texto, str) or not texto.strip():
        return []
    t = texto.lower()
    # En el orden en que aparecen en el texto ("Akamai, Cloudflare" → Akamai primero).
    posiciones = []
    for patron, empresa in EMPRESAS:
        m = re.search(patron, t)
        if m:
            posiciones.append((m.start(), empresa))
    return [e for _, e in sorted(posiciones)] or ["Otra"]
