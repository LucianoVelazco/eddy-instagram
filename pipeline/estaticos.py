"""Carruseles (1080x1350), posts (1080x1350) y stories (1080x1920) con la marca Eddy."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from . import graficos as G
from . import marca as M

CW, CH = 1080, 1350
VERDE_CLARO = (205, 232, 220)


def _color_modulo(pieza: dict):
    return M.MODULOS.get((pieza.get("modulo") or "correccion").strip().lower(), M.AZUL)


def _puntos(im, actual: int, total: int, y: int, color, apagado):
    d = ImageDraw.Draw(im)
    ancho = total * 22 + (total - 1) * 10
    x = (CW - ancho) // 2
    for i in range(total):
        c = color if i == actual else apagado
        w = 34 if i == actual else 22
        d.rounded_rectangle((x, y, x + w, y + 12), 6, fill=c)
        x += w + 10


def lamina_portada(pieza: dict, lam: dict, total: int) -> Image.Image:
    im = G.degradado(CW, CH, M.AZUL, M.TURQUESA)
    G.pegar_logo(im, 72, 76, 56, sobre_oscuro=True)
    sobre = (lam.get("sobretitulo") or pieza.get("pilar") or "").upper()
    if sobre:
        ImageDraw.Draw(im).text((72, 200), sobre, font=M.inter(30, "semibold"), fill=VERDE_CLARO)
    f = G.ajustar_fuente(lam["titulo"], lambda s: M.poppins(s, "bold"), 96, 56, 760, 5, alto_max=560)
    y = G.dibujar_texto(im, lam["titulo"], f, (72, 250, 832, 820), M.BLANCO, VERDE_CLARO,
                        alinear="izquierda", vertical="arriba")
    if lam.get("texto"):
        G.dibujar_texto(im, lam["texto"], M.inter(36, "regular"), (72, y + 24, 700, y + 220), M.BLANCO,
                        alinear="izquierda", vertical="arriba", interlineado=1.35)
    sp = G.sprite(0, True, 520)
    im.paste(sp, (CW - 520 + 70, CH - 560), sp)
    G.pastilla(im, 72, CH - 150, "Desliza  →", 30, M.BLANCO, M.AZUL_OSCURO)
    _puntos(im, 0, total, CH - 56, M.BLANCO, (120, 160, 200))
    return im


def lamina_interior(pieza: dict, lam: dict, n: int, total: int) -> Image.Image:
    color = _color_modulo(pieza)
    im = G.fondo_claro(CW, CH)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 14, CH), fill=color)
    d.ellipse((72, 80, 172, 180), fill=color)
    d.text((122, 130), str(n), font=M.poppins(52, "bold"), fill=M.BLANCO, anchor="mm")
    lg = G.logo(40)
    im.paste(lg, (CW - 72 - lg.width, 110), lg)
    f = G.ajustar_fuente(lam["titulo"], lambda s: M.poppins(s, "bold"), 76, 46, 936, 3, alto_max=320)
    alto_t = G.alto_texto(lam["titulo"], f, 936)
    ft, alto_c = None, 0
    if lam.get("texto"):
        ft = G.ajustar_fuente(lam["texto"], lambda s: M.inter(s, "regular"), 46, 30, 936, 9,
                              alto_max=CH - 420 - alto_t, interlineado=1.45)
        alto_c = 44 + G.alto_texto(lam["texto"], ft, 936, 1.45)
    # bloque centrado en el área útil, un poco hacia arriba
    y0 = 230 + max(0, int((CH - 160 - 230 - alto_t - alto_c) * 0.4))
    y = G.dibujar_texto(im, lam["titulo"], f, (72, y0, 1008, y0 + alto_t), M.TINTA, color, alinear="izquierda",
                        vertical="arriba")
    if ft:
        G.dibujar_texto(im, lam["texto"], ft, (72, y + 44, 1008, CH - 160), M.CUERPO, color,
                        alinear="izquierda", vertical="arriba", interlineado=1.45)
    _puntos(im, n, total, CH - 70, color, M.LINEA)
    return im


def lamina_cta(pieza: dict, lam: dict, total: int) -> Image.Image:
    im = Image.new("RGB", (CW, CH), M.BLANCO)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, CW, 14), fill=M.AZUL)
    sp = G.avatar_circulo(2, True, 300)
    im.paste(sp, ((CW - 300) // 2, 110), sp)
    titulo = lam.get("titulo") or M.PROMESA
    f = G.ajustar_fuente(titulo, lambda s: M.poppins(s, "bold"), 66, 44, 900, 3, alto_max=260)
    y = G.dibujar_texto(im, titulo, f, (90, 450, 990, 720), M.TINTA, M.AZUL)
    y = G.boton_cta(im, CW // 2, max(y + 40, 760), lam.get("boton") or f"Pruébalo en {M.WEB}", 46)
    sub = lam.get("texto") or "Guarda este post y compártelo con un colega."
    G.dibujar_texto(im, sub, M.inter(36, "medium"), (120, y + 40, 960, y + 200), M.SUAVE, interlineado=1.35)
    G.pegar_logo(im, (CW - 190) // 2, CH - 150, 52)
    _puntos(im, total - 1, total, CH - 56, M.AZUL, M.LINEA)
    return im


def carrusel(pieza: dict, contenido: dict, salida: Path) -> dict:
    salida.mkdir(parents=True, exist_ok=True)
    laminas = contenido["laminas"]
    total = len(laminas) + 1  # + lámina final de CTA
    archivos = []
    for i, lam in enumerate(laminas):
        im = lamina_portada(pieza, lam, total) if i == 0 else lamina_interior(pieza, lam, i, total)
        nombre = f"lamina_{i + 1:02d}.jpg"
        im.save(salida / nombre, "JPEG", quality=92)
        archivos.append(nombre)
    cta = lamina_cta(pieza, contenido.get("cta", {}), total)
    nombre = f"lamina_{total:02d}.jpg"
    cta.save(salida / nombre, "JPEG", quality=92)
    archivos.append(nombre)
    avisos = []
    if not 2 <= len(archivos) <= 10:
        avisos.append(f"El carrusel tiene {len(archivos)} láminas; la API de Instagram acepta de 2 a 10.")
    return {"archivos": archivos, "avisos": avisos}


def post(pieza: dict, contenido: dict, salida: Path) -> dict:
    """Post de una imagen: frase o dato grande."""
    salida.mkdir(parents=True, exist_ok=True)
    im = G.degradado(CW, CH, M.AZUL, M.TURQUESA)
    G.pegar_logo(im, 72, 76, 56, sobre_oscuro=True)
    frase = contenido["frase"]
    f = G.ajustar_fuente(frase, lambda s: M.poppins(s, "bold"), 92, 50, 936, 6, alto_max=560)
    y = G.dibujar_texto(im, frase, f, (72, 220, 1008, 780), M.BLANCO, VERDE_CLARO, alinear="izquierda",
                        vertical="centro")
    if contenido.get("subtitulo"):
        G.dibujar_texto(im, contenido["subtitulo"], M.inter(38, "medium"), (72, 800, 700, 1000), M.BLANCO,
                        alinear="izquierda", vertical="arriba", interlineado=1.35)
    sp = G.sprite(0, True, 500)
    im.paste(sp, (CW - 500 + 60, CH - 540), sp)
    G.pastilla(im, 72, CH - 150, M.WEB, 32, M.NARANJA, M.SOBRE_NARANJA)
    im.save(salida / "post.jpg", "JPEG", quality=92)
    return {"archivos": ["post.jpg"], "avisos": []}


def story(pieza: dict, contenido: dict, salida: Path) -> dict:
    """Story 1080x1920 con una pregunta o mensaje (los stickers de encuesta se agregan en la app)."""
    salida.mkdir(parents=True, exist_ok=True)
    im = G.degradado(1080, 1920, M.AZUL, M.TURQUESA)
    G.pegar_logo(im, 72, 300, 60, sobre_oscuro=True)
    f = G.ajustar_fuente(contenido["frase"], lambda s: M.poppins(s, "bold"), 96, 56, 936, 5, alto_max=560)
    G.dibujar_texto(im, contenido["frase"], f, (72, 420, 1008, 980), M.BLANCO, VERDE_CLARO)
    sp = G.sprite(0, True, 600)
    im.paste(sp, (240, 1060), sp)
    im.save(salida / "story.jpg", "JPEG", quality=92)
    return {"archivos": ["story.jpg"], "avisos": []}
