"""Publica en Instagram las piezas aprobadas cuya fecha y hora (Lima) ya llegó.

Uso:
    python -m pipeline.publicar             # publica lo que toca
    python -m pipeline.publicar --simular   # muestra qué publicaría, sin publicar

Variables de entorno: IG_USER_ID, IG_ACCESS_TOKEN, PUBLIC_BASE_URL
(PUBLIC_BASE_URL = dirección de GitHub Pages, p. ej. https://usuario.github.io/eddy-instagram)
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import timedelta

import requests

from . import calendario as C
from .marca import RAIZ
from .instagram import ErrorInstagram, Instagram

MEDIA = RAIZ / "docs" / "media"
VENTANA = timedelta(hours=72)   # si se pasó más de esto, no se publica tarde: queda "vencido"
MAX_INTENTOS = 3


def _url(base: str, id_: str, archivo: str) -> str:
    return f"{base.rstrip('/')}/media/{id_}/{archivo}"


def _disponible(url: str) -> bool:
    try:
        return requests.head(url, timeout=30, allow_redirects=True).status_code == 200
    except requests.RequestException:
        return False


def publicar_pieza(ig: Instagram | None, base: str, fila: dict, simular: bool) -> tuple[str, str]:
    meta = json.loads((MEDIA / fila["id"] / "meta.json").read_text(encoding="utf-8"))
    urls = [_url(base, fila["id"], a) for a in meta["archivos"]]
    if not simular and not all(_disponible(u) for u in urls):
        raise FileNotFoundError("Los archivos todavía no están en GitHub Pages; se reintenta en la próxima hora.")
    texto, fmt = meta["texto"], fila["formato"]
    if simular:
        print(f"  [simulación] {fmt}: {urls}\n  texto: {texto[:90]}…")
        return "simulado", ""
    if fmt in C.FORMATOS_REEL:
        mid = ig.reel(urls[0], texto, urls[1] if len(urls) > 1 else None)
    elif fmt == "carrusel":
        mid = ig.carrusel(urls, texto)
    elif fmt == "post":
        mid = ig.imagen(urls[0], texto)
    elif fmt == "story":
        mid = ig.story(urls[0])
    else:
        raise ValueError(f"Formato desconocido: {fmt}")
    return mid, ig.enlace(mid)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--simular", action="store_true")
    a = ap.parse_args()

    base = os.environ.get("PUBLIC_BASE_URL", "")
    ig = None if a.simular else Instagram()
    if not a.simular and not base:
        raise SystemExit("Falta la variable PUBLIC_BASE_URL (dirección de GitHub Pages).")

    filas = C.leer()
    ahora = C.ahora()
    cambios = 0
    for fila in filas:
        if fila["estado"] != "aprobado":
            continue
        cuando = C.momento(fila)
        if cuando > ahora:
            continue
        if ahora - cuando > VENTANA:
            fila["estado"] = "vencido"
            fila["notas"] = "No se publicó a tiempo; cambia la fecha y el estado a 'aprobado' para reprogramar."
            cambios += 1
            continue
        print(f"→ Publicando {fila['id']} ({fila['formato']}, programado {fila['fecha']} {fila['hora']})")
        try:
            mid, enlace = publicar_pieza(ig, base, fila, a.simular)
            if not a.simular:
                fila.update(estado="publicado", media_id=mid, permalink=enlace, notas="")
                cambios += 1
                print(f"  ✓ publicado: {enlace}")
        except FileNotFoundError as e:
            print(f"  … {e}")
        except (ErrorInstagram, requests.RequestException, ValueError) as e:
            n = int(fila["intentos"] or 0) + 1
            fila["intentos"] = str(n)
            fila["notas"] = str(e)[:300]
            if n >= MAX_INTENTOS:
                fila["estado"] = "error"
            cambios += 1
            print(f"  ✗ intento {n}: {e}")
    if cambios:
        C.guardar(filas)
    print(f"Fin: {cambios} cambios en el calendario.")


if __name__ == "__main__":
    main()
