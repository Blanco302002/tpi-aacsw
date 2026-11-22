"""
qr.py — makes the QR code for the explorer slide.

Usage (after deploying explorador/ to Vercel or similar):
    pip install qrcode
    python presentacion/qr.py https://your-explorer.vercel.app
    node presentacion/generar_pptx.js      (the QR replaces the placeholder on the "What goes dark for you?" slide)
"""

import sys
from pathlib import Path

import qrcode

if len(sys.argv) != 2 or not sys.argv[1].startswith("http"):
    sys.exit("Usage: python presentacion/qr.py https://your-explorer-url")

url = sys.argv[1]
img = qrcode.make(url, box_size=20, border=2)
salida = Path(__file__).resolve().parent / "qr.png"
img.save(salida)
(salida.parent / "qr_url.txt").write_text(url, encoding="utf-8")
print(f"OK {salida.name} -> {url}")
