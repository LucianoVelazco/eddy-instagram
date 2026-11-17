"""Lectura y escritura del calendario editorial (calendario/calendario.csv)."""
from __future__ import annotations

import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .marca import RAIZ

ARCHIVO = RAIZ / "calendario" / "calendario.csv"
CAMPOS = ["id", "fecha", "hora", "formato", "pilar", "modulo", "bondad", "titulo", "demo",
          "estado", "intentos", "media_id", "permalink", "notas"]
LIMA = timezone(timedelta(hours=-5))  # Perú no usa horario de verano

# Estados: pendiente -> aprobado (al hacer merge del PR) -> publicado | error | pausado | vencido
FORMATOS_REEL = {"reel_avatar", "reel_demo", "reel_faq", "reel_antes_despues"}
FORMATOS = FORMATOS_REEL | {"carrusel", "post", "story"}


def leer(ruta: Path = ARCHIVO) -> list[dict]:
    with open(ruta, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    for fila in filas:
        for c in CAMPOS:
            fila.setdefault(c, "")
            fila[c] = (fila[c] or "").strip()
    return filas


def guardar(filas: list[dict], ruta: Path = ARCHIVO):
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)


def momento(fila: dict) -> datetime:
    """Fecha y hora de publicación (hora de Lima)."""
    return datetime.strptime(f"{fila['fecha']} {fila['hora'] or '19:00'}", "%Y-%m-%d %H:%M").replace(tzinfo=LIMA)


def ahora() -> datetime:
    return datetime.now(LIMA)
