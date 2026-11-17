"""Utilidades de dibujo con la marca Eddy: degradados, texto enriquecido, logo, botones y avatar."""
from __future__ import annotations

from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

from . import marca as M


# ---------- fondos ----------

def degradado(w: int, h: int, c1, c2, diagonal: bool = True) -> Image.Image:
    """Degradado lineal de c1 a c2 (diagonal de arriba-izquierda a abajo-derecha, o vertical)."""
    import numpy as np
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    t = (x / max(1, w - 1) + y / max(1, h - 1)) / 2 if diagonal else y / max(1, h - 1)
    a, b = np.array(c1, np.float32), np.array(c2, np.float32)
    arr = a + (b - a) * t[..., None]
    return Image.fromarray(arr.round().astype("uint8"), "RGB")


def fondo_claro(w: int, h: int) -> Image.Image:
    """Fondo claro con dos manchas suaves de azul y verde."""
    im = Image.new("RGB", (w, h), M.FONDO)
    capa = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = int(w * 0.55)
    d.ellipse((w - r * 0.9, -r * 0.55, w + r * 1.1, r * 1.45), fill=(*M.AZUL_50, 255))
    d.ellipse((-r * 1.0, h - r * 1.1, r * 1.0, h + r * 0.9), fill=(*M.VERDE_50, 255))
    im.paste(capa, (0, 0), capa)
    return im


# ---------- texto ----------

def _tokens(texto: str):
    """Divide en palabras; las que van entre *asteriscos* se resaltan."""
    out, resaltado = [], False
    for parte in texto.replace("**", "*").split("*"):
        for i, palabra in enumerate(parte.split()):
            # la puntuación pegada al cierre de un resaltado (p. ej. "*enseñar*,") va con la palabra anterior
            if i == 0 and out and palabra[0] in ",.;:!?)»" and not parte.startswith(" "):
                previa, res_prev = out[-1]
                out[-1] = (previa + palabra, res_prev)
                continue
            out.append((palabra, resaltado))
        resaltado = not resaltado
    return out


def envolver(texto: str, fuente, ancho_max: int):
    lineas, actual = [], []
    espacio = fuente.getlength(" ")
    ancho = 0.0
    for palabra, res in _tokens(texto):
        w = fuente.getlength(palabra)
        if actual and ancho + espacio + w > ancho_max:
            lineas.append(actual)
            actual, ancho = [], 0.0
        ancho += (espacio if actual else 0) + w
        actual.append((palabra, res))
    if actual:
        lineas.append(actual)
    return lineas


def ajustar_fuente(texto: str, crear_fuente, tam_max: int, tam_min: int, ancho_max: int, max_lineas: int,
                   alto_max: int | None = None, interlineado: float = 1.0):
    """Busca el tamaño más grande que entra en max_lineas (y en alto_max, si se indica)."""
    tam = tam_max
    while tam > tam_min:
        f = crear_fuente(tam)
        n = len(envolver(texto, f, ancho_max))
        asc, desc = f.getmetrics()
        if n <= max_lineas and (alto_max is None or n * int((asc + desc) * interlineado) <= alto_max):
            return f
        tam -= 2
    return crear_fuente(tam_min)


def alto_texto(texto: str, fuente, ancho_max: int, interlineado: float = 1.0) -> int:
    asc, desc = fuente.getmetrics()
    return int((asc + desc) * interlineado) * len(envolver(texto, fuente, ancho_max))


def dibujar_texto(img: Image.Image, texto: str, fuente, caja, color, color_resaltado=None,
                  alinear: str = "centro", interlineado: float = 1.0, vertical: str = "centro") -> int:
    """Dibuja texto envuelto dentro de caja=(x0,y0,x1,y1). Devuelve la y final."""
    x0, y0, x1, y1 = caja
    d = ImageDraw.Draw(img)
    lineas = envolver(texto, fuente, x1 - x0)
    asc, desc = fuente.getmetrics()
    alto_linea = int((asc + desc) * interlineado)
    alto_total = alto_linea * len(lineas)
    if vertical == "centro":
        y = y0 + max(0, (y1 - y0 - alto_total) // 2)
    elif vertical == "abajo":
        y = y1 - alto_total
    else:
        y = y0
    espacio = fuente.getlength(" ")
    color_resaltado = color_resaltado or color
    for linea in lineas:
        ancho = sum(fuente.getlength(p) for p, _ in linea) + espacio * (len(linea) - 1)
        if alinear == "centro":
            x = x0 + (x1 - x0 - ancho) / 2
        elif alinear == "derecha":
            x = x1 - ancho
        else:
            x = x0
        for palabra, res in linea:
            d.text((x, y), palabra, font=fuente, fill=color_resaltado if res else color)
            x += fuente.getlength(palabra) + espacio
        y += alto_linea
    return y


# ---------- piezas de marca ----------

def logo(alto: int, sobre_oscuro: bool = False) -> Image.Image:
    """Logotipo 'Eddy' en Poppins Bold con el degradado azul→verde (o blanco sobre fondo oscuro)."""
    f = M.poppins(alto, "bold")
    l, t, r, b = f.getbbox("Eddy")
    w, h = r + 4, b + 4
    mascara = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mascara).text((0, 0), "Eddy", font=f, fill=255)
    if sobre_oscuro:
        relleno = Image.new("RGB", (w, h), M.BLANCO)
    else:  # degradado horizontal: azul a la izquierda, verde a la derecha
        mascara_grad = Image.linear_gradient("L").rotate(90).resize((w, h))
        relleno = Image.composite(Image.new("RGB", (w, h), M.VERDE), Image.new("RGB", (w, h), M.AZUL), mascara_grad)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(relleno, (0, 0), mascara)
    return out.crop((l, t, r, b))


def pegar_logo(img: Image.Image, x: int, y: int, alto: int, sobre_oscuro: bool = False, con_ia: bool = True):
    lg = logo(alto, sobre_oscuro)
    img.paste(lg, (x, y), lg)
    if con_ia:
        fe = M.poppins(alto, "bold")
        base = fe.getbbox("E")[3] - fe.getbbox("Eddy")[1]   # línea base de la palabra Eddy
        f = M.poppins(int(alto * 0.72), "semibold")
        color = M.BLANCO if sobre_oscuro else M.TINTA
        ImageDraw.Draw(img).text((x + lg.width + int(alto * 0.2), y + base), "IA", font=f, fill=color, anchor="ls")
    return lg.width


def rect_redondeado(img: Image.Image, caja, radio: int, relleno, borde=None, ancho_borde: int = 0, sombra: bool = False):
    if sombra:
        x0, y0, x1, y1 = caja
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 14, x1, y1 + 14), radio, fill=(15, 23, 42, 46))
        sh = sh.filter(ImageFilter.GaussianBlur(22))
        img.paste(sh, (0, 0), sh)
    ImageDraw.Draw(img).rounded_rectangle(caja, radio, fill=relleno, outline=borde, width=ancho_borde)


def boton_cta(img: Image.Image, centro_x: int, y: int, texto: str, tam: int = 46):
    """Botón naranja de acción (texto oscuro encima, nunca blanco)."""
    f = M.poppins(tam, "semibold")
    w = int(f.getlength(texto)) + tam * 2
    h = int(tam * 2.1)
    x0 = centro_x - w // 2
    rect_redondeado(img, (x0, y, x0 + w, y + h), h // 2, M.NARANJA, sombra=True)
    ImageDraw.Draw(img).text((centro_x, y + h // 2), texto, font=f, fill=M.SOBRE_NARANJA, anchor="mm")
    return y + h


def pastilla(img: Image.Image, x: int, y: int, texto: str, tam: int, fondo, color, anclar: str = "izq"):
    f = M.inter(tam, "semibold")
    w = int(f.getlength(texto)) + tam * 2
    h = int(tam * 2.0)
    if anclar == "centro":
        x = x - w // 2
    ImageDraw.Draw(img).rounded_rectangle((x, y, x + w, y + h), h // 2, fill=fondo)
    ImageDraw.Draw(img).text((x + w // 2, y + h // 2), texto, font=f, fill=color, anchor="mm")
    return x + w, y + h


# ---------- avatar ----------

def _asegurar_sprites():
    """Si faltan los PNG del Profe Eddy, los genera desde su SVG (avatar/profe_eddy.py)."""
    if (M.SPRITES / "boca2_ojos_cerrados.png").exists():
        return
    import importlib.util
    spec = importlib.util.spec_from_file_location("profe_eddy", M.RAIZ / "avatar" / "profe_eddy.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.build_sprites(M.SPRITES)


@lru_cache(maxsize=64)
def sprite(boca: int, ojos_abiertos: bool, ancho: int) -> Image.Image:
    _asegurar_sprites()
    tag = "abiertos" if ojos_abiertos else "cerrados"
    im = Image.open(M.SPRITES / f"boca{boca}_ojos_{tag}.png").convert("RGBA")
    alto = int(im.height * ancho / im.width)
    return im.resize((ancho, alto), Image.LANCZOS)


@lru_cache(maxsize=64)
def avatar_circulo(boca: int, ojos_abiertos: bool, diametro: int, fondo=M.AZUL_50, borde=M.BLANCO) -> Image.Image:
    """Cabeza del Profe Eddy dentro de un círculo (para el recuadro sobre la demo)."""
    full = sprite(boca, ojos_abiertos, 900)
    s = full.width / 600  # escala respecto al SVG original de 600x720
    cab = full.crop((int(70 * s), int(80 * s), int(530 * s), int(540 * s))).resize((diametro, diametro), Image.LANCZOS)
    out = Image.new("RGBA", (diametro, diametro), (0, 0, 0, 0))
    disco = Image.new("RGBA", (diametro, diametro), (*fondo, 255))
    mascara = Image.new("L", (diametro, diametro), 0)
    ImageDraw.Draw(mascara).ellipse((0, 0, diametro - 1, diametro - 1), fill=255)
    disco.alpha_composite(cab)
    out.paste(disco, (0, 0), mascara)
    ImageDraw.Draw(out).ellipse((3, 3, diametro - 4, diametro - 4), outline=borde, width=10)
    ImageDraw.Draw(out).ellipse((0, 0, diametro - 1, diametro - 1), outline=M.AZUL, width=4)
    return out
