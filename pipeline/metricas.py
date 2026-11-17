"""Reporte semanal de métricas de lo publicado (metricas/metricas.csv y metricas/reporte.md)."""
from __future__ import annotations

import csv
from collections import defaultdict

from . import calendario as C
from .instagram import Instagram
from .marca import RAIZ

CARPETA = RAIZ / "metricas"
METRICAS = ["reach", "views", "saved", "shares", "likes", "comments", "total_interactions"]
NOMBRES = {"reach": "Alcance", "views": "Reproducciones", "saved": "Guardados", "shares": "Compartidos",
           "likes": "Me gusta", "comments": "Comentarios", "total_interactions": "Interacciones"}


def main():
    ig = Instagram()
    hoy = C.ahora().date().isoformat()
    filas = [f for f in C.leer() if f["estado"] == "publicado" and f["media_id"]]
    CARPETA.mkdir(exist_ok=True)
    historico = CARPETA / "metricas.csv"
    nuevo = not historico.exists()
    registros = []
    for f in filas:
        m = ig.metricas(f["media_id"], METRICAS)
        registros.append({"fecha_reporte": hoy, "id": f["id"], "fecha_pub": f["fecha"], "formato": f["formato"],
                          "pilar": f["pilar"], **{k: m.get(k) for k in METRICAS}, "permalink": f["permalink"]})
    with open(historico, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["fecha_reporte", "id", "fecha_pub", "formato", "pilar", *METRICAS, "permalink"])
        if nuevo:
            w.writeheader()
        w.writerows(registros)

    def num(v):
        return v if isinstance(v, (int, float)) else 0

    registros.sort(key=lambda r: num(r["reach"]), reverse=True)
    lineas = [f"# Reporte de métricas · {hoy}", "",
              f"{len(registros)} publicaciones medidas. Ordenadas por alcance.", "",
              "| Pieza | Formato | Pilar | " + " | ".join(NOMBRES[k] for k in METRICAS) + " |",
              "|---|---|---|" + "---:|" * len(METRICAS)]
    for r in registros:
        celdas = " | ".join("" if r[k] is None else str(r[k]) for k in METRICAS)
        lineas.append(f"| [{r['id']}]({r['permalink']}) | {r['formato']} | {r['pilar']} | {celdas} |")
    por_pilar = defaultdict(list)
    for r in registros:
        por_pilar[r["pilar"]].append(r)
    if por_pilar:
        lineas += ["", "## Promedio por pilar", "", "| Pilar | Piezas | Alcance medio | Guardados medios | Compartidos medios |",
                   "|---|---:|---:|---:|---:|"]
        for pilar, rs in sorted(por_pilar.items(), key=lambda kv: -sum(num(x["reach"]) for x in kv[1]) / len(kv[1])):
            n = len(rs)
            lineas.append(f"| {pilar} | {n} | {sum(num(x['reach']) for x in rs) / n:.0f} | "
                          f"{sum(num(x['saved']) for x in rs) / n:.1f} | {sum(num(x['shares']) for x in rs) / n:.1f} |")
        lineas += ["", "Regla del pipeline: el pilar con mejor promedio gana un espacio más en el calendario del mes siguiente."]
    (CARPETA / "reporte.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"Reporte listo: {len(registros)} publicaciones.")


if __name__ == "__main__":
    main()
