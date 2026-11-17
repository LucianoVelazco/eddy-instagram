"""Línea de marca de Eddy IA: colores, tipografías y frases fijas.

Valores tomados del design system de Eddy (colores muestreados del logotipo).
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PIL import ImageFont

RAIZ = Path(__file__).resolve().parent.parent
FUENTES = RAIZ / "marca" / "fuentes"
SPRITES = RAIZ / "avatar" / "sprites"

# Colores de marca
AZUL = (47, 104, 176)          # #2F68B0 primario, inicio del logo
AZUL_OSCURO = (39, 87, 148)    # #275794
TURQUESA = (61, 133, 157)      # #3D859D centro del degradado
VERDE = (88, 179, 137)         # #58B389 secundario, final del logo
VERDE_TEXTO = (56, 121, 92)    # #38795C verde para texto sobre claro
NARANJA = (240, 160, 75)       # #F0A04B solo para el CTA
SOBRE_NARANJA = (58, 36, 16)   # #3A2410 texto sobre el naranja
FONDO = (248, 250, 252)        # #F8FAFC
BLANCO = (255, 255, 255)
TINTA = (11, 13, 18)           # #0B0D12 titulares
CUERPO = (71, 85, 105)         # #475569 texto de cuerpo
SUAVE = (100, 116, 139)        # #64748B metadatos
LINEA = (226, 232, 240)        # #E2E8F0
AZUL_50 = (240, 244, 249)
VERDE_50 = (230, 244, 237)

# Color por módulo del producto
MODULOS = {
    "correccion": (51, 102, 224),   # Corrección con IA
    "contenido": (47, 138, 69),     # Creación de contenido
    "plan": (132, 65, 224),         # Plan académico
    "gestion": (194, 82, 31),       # Gestión por clases
}

PROMESA = "Tu tiempo es para enseñar, no para corregir exámenes."
WEB = "eddyai.lat"
CIERRE_VOZ = "Tu tiempo es para enseñar, no para corregir exámenes. Pruébalo en eddyai punto lat."
HASHTAGS_BASE = ["#EddyIA", "#docentes", "#evaluación"]

_PESOS_INTER = {"regular": 400, "medium": 500, "semibold": 600, "bold": 700}
_ARCHIVOS_POPPINS = {
    "regular": "Poppins-Regular.ttf", "medium": "Poppins-Medium.ttf",
    "semibold": "Poppins-SemiBold.ttf", "bold": "Poppins-Bold.ttf",
}


_URL_FUENTES = "https://raw.githubusercontent.com/google/fonts/main/ofl"
_DESCARGAS = {**{a: f"{_URL_FUENTES}/poppins/{a}" for a in _ARCHIVOS_POPPINS.values()},
              "Inter.ttf": f"{_URL_FUENTES}/inter/Inter%5Bopsz,wght%5D.ttf"}


def _fuente(nombre: str) -> str:
    """Ruta a la fuente; si no está, la descarga de Google Fonts (licencia OFL)."""
    ruta = FUENTES / nombre
    if not ruta.exists():
        import requests
        FUENTES.mkdir(parents=True, exist_ok=True)
        r = requests.get(_DESCARGAS[nombre], timeout=60)
        r.raise_for_status()
        ruta.write_bytes(r.content)
    return str(ruta)


@lru_cache(maxsize=256)
def poppins(size: int, peso: str = "bold") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(_fuente(_ARCHIVOS_POPPINS[peso]), size)


@lru_cache(maxsize=256)
def inter(size: int, peso: str = "regular") -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(_fuente("Inter.ttf"), size)
    try:
        f.set_variation_by_axes([min(32, max(14, size)), _PESOS_INTER[peso]])
    except Exception:  # fuente sin ejes variables
        pass
    return f


def mezclar(c1, c2, t: float):
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(c1, c2))
