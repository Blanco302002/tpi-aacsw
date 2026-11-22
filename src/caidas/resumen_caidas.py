"""
resumen_caidas.py
Resume cada caída en pocos números, a partir de los CSV de Radar
(src/caidas/radar_trafico.py). No usa internet.

Para cada caída y fuente (http, netflows) compara el tráfico durante la
caída contra la misma hora de la semana anterior, y contra las horas
previas (para saber si ese día ya venía raro).

Salida: data/resultados/resumen_caidas.csv

Uso:
    python src/caidas/resumen_caidas.py
"""

import pandas as pd

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # src/: para importar comun y los otros temas

from comun import CSV_ENC, FUENTES, RESULTADOS

# Ventanas de la caída en UTC (Argentina = UTC-3), según cada postmortem.
#   Cloudflare: 11:20 empiezan los errores; 17:06 todo normal.
#   AWS: 06:48 (23:48 PDT del 19/10) empiezan los errores en us-east-1; ~22:00 todo restaurado.
#   CrowdStrike: 04:09 sale la actualización defectuosa; 05:27 se retira, pero las
#   computadoras afectadas siguieron caídas horas o días (se toman 12 h).
CAIDAS = {
    "cloudflare_2025-11-18":  ("2025-11-18T11:20:00Z", "2025-11-18T17:06:00Z"),
    "aws_2025-10-20":         ("2025-10-20T06:48:00Z", "2025-10-20T22:00:00Z"),
    "crowdstrike_2024-07-19": ("2024-07-19T04:09:00Z", "2024-07-19T16:09:00Z"),
}


def hora_ar(ts):
    return (ts - pd.Timedelta(hours=3)).strftime("%d/%m %H:%M")


def main():
    filas = []
    for evento, (ini, fin) in CAIDAS.items():
        ruta = FUENTES / f"radar_{evento}.csv"
        if not ruta.exists():
            print(f"Falta {ruta.name}: corré primero radar_trafico.py")
            continue
        d = pd.read_csv(ruta)
        d["ts"] = pd.to_datetime(d["timestamp_utc"], utc=True)
        a, b = pd.Timestamp(ini), pd.Timestamp(fin)
        for fuente, g in d.dropna(subset=["dif_pct"]).groupby("fuente"):
            dentro = g[(g.ts >= a) & (g.ts <= b)]
            antes = g[(g.ts >= a - pd.Timedelta(hours=6)) & (g.ts < a)]
            peor = dentro.loc[dentro["dif_pct"].idxmin()]
            filas.append({
                "evento": evento,
                "fuente": fuente,
                "inicio_ar": hora_ar(a),
                "fin_ar": hora_ar(b),
                "dif_pct_6h_antes": round(antes["dif_pct"].mean(), 1),
                "dif_pct_promedio_caida": round(dentro["dif_pct"].mean(), 1),
                "dif_pct_peor_momento": peor["dif_pct"],
                "peor_momento_ar": hora_ar(peor["ts"]),
            })
    res = pd.DataFrame(filas)
    res.to_csv(RESULTADOS / "resumen_caidas.csv", index=False, encoding=CSV_ENC)
    print("Tráfico de Argentina vs. misma hora de la semana anterior (%):\n")
    print(res.to_string(index=False))
    print("\nOK data/resultados/resumen_caidas.csv")


if __name__ == "__main__":
    main()
