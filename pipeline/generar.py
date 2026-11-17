"""Genera las piezas pendientes de un rango de fechas y prepara el resumen para aprobarlas.

Uso:
    python -m pipeline.generar --desde 2026-11-23 --dias 7
    python -m pipeline.generar --ids s1-lun-reel,s1-mie-carrusel --forzar
    python -m pipeline.generar --proxima-semana        # (lo usa GitHub Actions)

Cada pieza queda en docs/media/<id>/ (GitHub Pages la sirve con un enlace público, que es lo que
Instagram necesita para descargarla) y su estado pasa a "aprobado" dentro del PR: al hacer merge
del PR, quedan aprobadas. Para frenar una pieza, cambia su estado a "pausado" en el PR antes del merge.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import traceback
from datetime import date, datetime, timedelta

from . import calendario as C
from . import contenido as K
from . import estaticos as E
from . import reel as R
from .marca import RAIZ

MEDIA = RAIZ / "docs" / "media"
RESUMEN = RAIZ / "revision" / "RESUMEN.md"


def generar_pieza(pieza: dict) -> dict:
    salida = MEDIA / pieza["id"]
    if salida.exists():
        shutil.rmtree(salida)
    contenido, origen, avisos = K.cargar(pieza)
    avisos += K.revisar(pieza, contenido)
    fmt = pieza["formato"]
    if fmt in C.FORMATOS_REEL:
        res = R.renderizar(pieza, contenido, salida, RAIZ)
    elif fmt == "carrusel":
        res = E.carrusel(pieza, contenido, salida)
    elif fmt == "post":
        res = E.post(pieza, contenido, salida)
    elif fmt == "story":
        res = E.story(pieza, contenido, salida)
    else:
        raise ValueError(f"Formato desconocido: {fmt}")
    meta = {
        "id": pieza["id"], "formato": fmt, "fecha": pieza["fecha"], "hora": pieza["hora"],
        "archivos": res["archivos"], "texto": K.texto_publicacion(contenido),
        "hooks_alternativos": contenido.get("hooks_alternativos", []),
        "origen_guion": origen, "avisos": avisos + res.get("avisos", []),
        "duracion_s": res.get("duracion_s"), "generado": datetime.now(C.LIMA).isoformat(timespec="minutes"),
    }
    (salida / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (salida / "texto.txt").write_text(meta["texto"], encoding="utf-8")
    return meta


def _resumen(metas: list[dict], errores: list[tuple], rama: str | None) -> str:
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    def url(id_, archivo):
        if repo and rama:
            return f"https://raw.githubusercontent.com/{repo}/{rama}/docs/media/{id_}/{archivo}"
        return f"../docs/media/{id_}/{archivo}"

    lineas = ["# Piezas para aprobar", "",
              "Al hacer **merge** de este PR, las piezas de abajo quedan **aprobadas** y se publicarán solas "
              "en su fecha y hora (hora de Lima).", "",
              "- Para **frenar** una pieza: en este PR edita `calendario/calendario.csv` y cambia su estado a `pausado`.",
              "- Para **corregir** un texto o guion: edita `contenido/<id>.json` en `main`, cierra este PR y "
              "vuelve a correr *1 · Generar piezas* con ese id.", ""]
    for m in metas:
        lineas += [f"## {m['fecha']} {m['hora']} · {m['formato']} · `{m['id']}`", ""]
        if m["formato"] in C.FORMATOS_REEL:
            lineas += [f"<img src=\"{url(m['id'], 'portada.jpg')}\" width=\"220\">", "",
                       f"[Ver el reel ({m.get('duracion_s')} s)]({url(m['id'], 'reel.mp4')})", ""]
        else:
            imgs = " ".join(f"<img src=\"{url(m['id'], a)}\" width=\"180\">" for a in m["archivos"])
            lineas += [imgs, ""]
        lineas += ["**Texto de la publicación:**", "", "```text", m["texto"], "```", ""]
        if m.get("hooks_alternativos"):
            lineas += ["Hooks alternativos: " + " · ".join(m["hooks_alternativos"]), ""]
        if m["avisos"]:
            lineas += ["**Revisar:**", ""] + [f"- [ ] {a}" for a in m["avisos"]] + [""]
    if errores:
        lineas += ["## Errores", ""] + [f"- `{i}`: {e}" for i, e in errores]
    return "\n".join(lineas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde", help="AAAA-MM-DD (por defecto, hoy)")
    ap.add_argument("--dias", type=int, default=7)
    ap.add_argument("--proxima-semana", action="store_true", help="del próximo lunes al domingo")
    ap.add_argument("--ids", help="ids separados por coma")
    ap.add_argument("--forzar", action="store_true", help="regenera aunque no estén pendientes")
    ap.add_argument("--rama", help="rama del PR, para los enlaces de vista previa")
    a = ap.parse_args()

    hoy = datetime.now(C.LIMA).date()
    if a.proxima_semana:
        desde = hoy + timedelta(days=(7 - hoy.weekday()) % 7 or 7)
        dias = 7
    else:
        desde = date.fromisoformat(a.desde) if a.desde else hoy
        dias = a.dias
    hasta = desde + timedelta(days=dias - 1)
    ids = set(a.ids.split(",")) if a.ids else None

    filas = C.leer()
    metas, errores = [], []
    for fila in filas:
        if ids is not None:
            if fila["id"] not in ids:
                continue
        else:
            f = date.fromisoformat(fila["fecha"])
            if not (desde <= f <= hasta):
                continue
        if fila["estado"] == "publicado":
            continue
        if fila["estado"] not in ("pendiente", "") and not a.forzar:
            continue
        print(f"→ {fila['id']} ({fila['formato']})")
        try:
            metas.append(generar_pieza(fila))
            fila["estado"] = "aprobado"
            fila["intentos"] = "0"
            fila["notas"] = ""
        except Exception as e:
            traceback.print_exc()
            errores.append((fila["id"], f"{type(e).__name__}: {e}"))
    C.guardar(filas)
    RESUMEN.parent.mkdir(exist_ok=True)
    RESUMEN.write_text(_resumen(metas, errores, a.rama), encoding="utf-8")
    print(f"Listo: {len(metas)} piezas generadas, {len(errores)} con error. Resumen en revision/RESUMEN.md")
    if not metas and not errores:
        print("No había piezas pendientes en ese rango.")


if __name__ == "__main__":
    main()
