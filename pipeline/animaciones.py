"""Escenas animadas que ilustran cada bondad de Eddy (reemplazan a las grabaciones de pantalla).

Son ilustraciones con la marca, no capturas de la plataforma: muestran QUÉ hace Eddy sin inventar
pantallas reales. En el calendario o el guion se usan con  "anim:<nombre>"  (ver NOMBRES abajo).
Si existe una grabación real (demos/*.mp4), siempre se puede usar en su lugar.

Cada animación es una función (t, w, h) -> Image, con t entre 0 y 1 a lo largo de la escena.
Se diseñan para un lienzo de 1000x700 (letra grande, legible en el celular) y la esquina
inferior derecha queda libre porque ahí va el Profe Eddy.
"""
from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw

from . import marca as M

FONDO = (243, 247, 252)
TINTA = M.TINTA
SUAVE = M.SUAVE
AZUL = M.AZUL
VERDE = M.VERDE
VERDE_OSC = M.VERDE_TEXTO
NARANJA = (226, 114, 47)
NARANJA_OSC = (124, 45, 18)
NARANJA_TINTE = (253, 240, 230)
AZUL_TINTE = (234, 241, 253)
VERDE_TINTE = (233, 247, 236)
GRIS = (203, 213, 225)
TINTA_MANO = (30, 58, 138)
VERDE_MOD = (47, 138, 69)


# ---------- utilidades ----------

def _seg(t, a, b):
    if t <= a:
        return 0.0
    if t >= b:
        return 1.0
    x = (t - a) / (b - a)
    return x * x * (3 - 2 * x)


def _lienzo(w, h):
    im = Image.new("RGB", (w, h), FONDO)
    return im, ImageDraw.Draw(im, "RGBA")


def _check(d, cx, cy, r, p, color=VERDE):
    if p <= 0:
        return
    rr = r * min(1, p * 1.6)
    d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=color)
    if p > 0.4:
        q = min(1, (p - 0.4) / 0.6)
        a, b, c = (cx - r * 0.45, cy), (cx - r * 0.1, cy + r * 0.35), (cx + r * 0.5, cy - r * 0.35)
        if q < 0.5:
            k = q / 0.5
            pts = [a, (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)]
        else:
            k = (q - 0.5) / 0.5
            pts = [a, b, (b[0] + (c[0] - b[0]) * k, b[1] + (c[1] - b[1]) * k)]
        d.line(pts, fill=(255, 255, 255), width=max(4, int(r * 0.24)), joint="curve")


def _cruz(d, cx, cy, r, p):
    if p <= 0:
        return
    rr = r * min(1, p * 1.6)
    d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=NARANJA)
    if p > 0.5:
        k = r * 0.35
        d.line((cx - k, cy - k, cx + k, cy + k), fill=(255, 255, 255), width=max(4, int(r * 0.22)))
        d.line((cx - k, cy + k, cx + k, cy - k), fill=(255, 255, 255), width=max(4, int(r * 0.22)))


def _tarjeta(d, caja, relleno=(255, 255, 255), borde=GRIS, r=20, alfa=255):
    d.rounded_rectangle(caja, r, fill=(*relleno, alfa), outline=(*borde, alfa), width=3)


def _papel(d, x, y, w, h, lineas=6, alfa=255, semilla=1):
    _tarjeta(d, (x, y, x + w, y + h), r=12, alfa=alfa)
    rnd = random.Random(semilla)
    for i in range(lineas):
        ly = y + h * 0.12 + i * (h * 0.8) / max(1, lineas)
        lw = (w - 30) * rnd.uniform(0.5, 0.95)
        d.rounded_rectangle((x + 15, ly, x + 15 + lw, ly + max(5, h * 0.025)), 3, fill=(*GRIS, alfa))


def _pastilla(d, cx, cy, texto, fuente, fondo, color, alfa=255):
    w = fuente.getlength(texto) + 56
    h = fuente.size * 1.8
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), h / 2, fill=(*fondo, alfa))
    d.text((cx, cy), texto, font=fuente, fill=(*color, alfa), anchor="mm")


def _mano(d, x0, y0, largo, semilla):
    rnd = random.Random(semilla)
    pts, x = [], x0
    while x < x0 + largo:
        pts.append((x, y0 + math.sin(x * 0.18 + semilla) * 7 + rnd.uniform(-3, 3)))
        x += 6
    if len(pts) > 1:
        d.line(pts, fill=TINTA_MANO, width=4, joint="curve")


def _escribir(texto, p):
    return texto[: int(len(texto) * max(0.0, min(1.0, p)))]


def _envolver(texto, fuente, ancho):
    out, linea = [], ""
    for pal in texto.split():
        prueba = (linea + " " + pal).strip()
        if fuente.getlength(prueba) <= ancho:
            linea = prueba
        else:
            out.append(linea)
            linea = pal
    if linea:
        out.append(linea)
    return out


# ---------- animaciones (lienzo 1000 x 700) ----------

def lote(t, w, h):
    """Un lote de exámenes entra a Eddy y sale corregido."""
    im, d = _lienzo(w, h)
    n, notas = 6, [17, 15, 19, 14, 18, 16]
    tramos = [(0.06 + i * 0.12, 0.2 + i * 0.12) for i in range(n)]
    hechos = sum(1 for a, b in tramos if t >= b)
    for i in range(n - 1, -1, -1):
        if t < tramos[i][0]:
            _papel(d, 30 + i * 5, 150 + i * 8, 210, 290, 7, semilla=i)
    cx, cy, r = 420, 300, 105
    r2 = r + int(5 * math.sin(t * 40))
    d.ellipse((cx - r2 - 12, cy - r2 - 12, cx + r2 + 12, cy + r2 + 12), fill=(*VERDE, 70))
    d.ellipse((cx - r2, cy - r2, cx + r2, cy + r2), fill=AZUL)
    d.text((cx, cy), "Eddy", font=M.poppins(58, "bold"), fill=(255, 255, 255), anchor="mm")
    for i, (a, b) in enumerate(tramos):
        p = _seg(t, a, b)
        if 0 < p < 1:
            esc = 1 - 0.65 * p
            _papel(d, 30 + (cx - 100) * p, 150 + (cy - 230) * p, 210 * esc, 290 * esc, 6,
                   alfa=int(255 * (1 - 0.6 * p)), semilla=i)
    f, fn = M.inter(34, "semibold"), M.poppins(36, "bold")
    for i in range(hechos):
        y = 30 + i * 82
        q = _seg(t, tramos[i][1], tramos[i][1] + 0.08)
        _tarjeta(d, (590, y, 975, y + 68), r=16)
        d.text((612, y + 34), f"Examen {i + 1}", font=f, fill=TINTA, anchor="lm")
        d.text((880, y + 34), f"{notas[i]}/20", font=fn, fill=AZUL, anchor="rm")
        _check(d, 932, y + 34, 24, q)
    _pastilla(d, cx, cy + r + 80, f"{hechos} de {n} corregidos", M.poppins(34, "semibold"), VERDE_TINTE, VERDE_OSC)
    return im


def manuscrito(t, w, h):
    """Foto de un examen escrito a mano → lectura → resultado preliminar."""
    im, d = _lienzo(w, h)
    px, py, pw, ph = 30, 30, 430, 640
    _tarjeta(d, (px, py, px + pw, py + ph), r=12)
    d.text((px + 24, py + 26), "Examen · 3.º B", font=M.inter(28, "semibold"), fill=SUAVE)
    for q in range(3):
        y = py + 120 + q * 170
        d.text((px + 24, y - 6), f"{q + 1}.", font=M.poppins(34, "bold"), fill=TINTA)
        for k in range(3):
            _mano(d, px + 80, y + 14 + k * 42, pw - 120 - k * 70, semilla=q * 3 + k)
    pf = _seg(t, 0.0, 0.2) * (1 - _seg(t, 0.32, 0.42))
    if pf > 0:
        m, a = int(30 * (1 - pf)), int(255 * pf)
        d.rounded_rectangle((px - 14 - m, py - 14 - m, px + pw + 14 + m, py + ph + 14 + m), 40,
                            outline=(17, 24, 39, a), width=16)
    fl = _seg(t, 0.24, 0.27) * (1 - _seg(t, 0.27, 0.34))
    if fl > 0:
        d.rectangle((px, py, px + pw, py + ph), fill=(255, 255, 255, int(230 * fl)))
    sc = _seg(t, 0.34, 0.58)
    if 0 < sc < 1:
        y = py + ph * sc
        d.rectangle((px, y - 40, px + pw, y), fill=(*VERDE, 55))
        d.line((px, y, px + pw, y), fill=VERDE, width=5)
    rp = _seg(t, 0.56, 0.64)
    if rp > 0:
        x0 = px + pw + 30
        _tarjeta(d, (x0, py, w - 25, py + 440), alfa=int(255 * rp))
        d.text((x0 + 26, py + 30), "Resultado", font=M.poppins(38, "bold"), fill=TINTA)
        d.text((x0 + 26, py + 78), "preliminar", font=M.poppins(38, "bold"), fill=TINTA)
        for q, ok in enumerate([True, True, False]):
            y = py + 190 + q * 85
            qp = _seg(t, 0.64 + q * 0.07, 0.72 + q * 0.07)
            if qp > 0:
                d.text((x0 + 26, y), f"Pregunta {q + 1}", font=M.inter(34, "medium"), fill=TINTA, anchor="lm")
                (_check if ok else _cruz)(d, w - 80, y, 28, qp)
    if t > 0.88:
        d.text((px + pw + 56, py + 470), "Tú revisas", font=M.poppins(36, "semibold"), fill=VERDE_OSC)
        d.text((px + pw + 56, py + 518), "y decides", font=M.poppins(36, "semibold"), fill=VERDE_OSC)
    return im


def semantico(t, w, h):
    """Dos respuestas con distintas palabras y la misma idea: ambas correctas."""
    im, d = _lienzo(w, h)
    _tarjeta(d, (25, 20, w - 25, 170), relleno=AZUL_TINTE, borde=AZUL_TINTE)
    d.text((50, 40), "Clave de respuesta", font=M.inter(26, "semibold"), fill=AZUL)
    clave = "La fotosíntesis transforma la luz en energía química."
    fk = M.inter(32, "medium")
    for k, linea in enumerate(_envolver(clave, fk, w - 100)):
        d.text((50, 80 + k * 40), linea, font=fk, fill=TINTA)
    resp = [("Alumno A", "Las plantas convierten la luz del sol en energía."),
            ("Alumno B", "Con la luz solar, la planta fabrica su alimento.")]
    f = M.inter(34, "regular")
    cw = (w - 25 * 2 - 24) // 2
    for i, (nombre, texto) in enumerate(resp):
        x0, y0 = 25 + i * (cw + 24), 195
        _tarjeta(d, (x0, y0, x0 + cw, h - 25))
        d.text((x0 + 24, y0 + 22), nombre, font=M.poppins(30, "bold"), fill=SUAVE)
        visible = _escribir(texto, _seg(t, 0.06 + i * 0.2, 0.3 + i * 0.2))
        for k, linea in enumerate(_envolver(visible, f, cw - 48)):
            d.text((x0 + 24, y0 + 84 + k * 46), linea, font=f, fill=TINTA)
        ok = _seg(t, 0.62 + i * 0.1, 0.74 + i * 0.1)
        if ok > 0:
            _check(d, x0 + cw - 46, y0 + 42, 28, ok)
        if ok >= 1 and i == 0:
            _pastilla(d, x0 + 130, h - 85, "Correcta", M.inter(30, "semibold"), VERDE_TINTE, VERDE_OSC)
    return im


def ajustar_nota(t, w, h):
    """El docente revisa el resultado preliminar y cambia una nota."""
    im, d = _lienzo(w, h)
    x0, y0, x1 = 25, 20, w - 25
    _tarjeta(d, (x0, y0, x1, h - 20))
    d.text((x0 + 30, y0 + 28), "Resultado · Alumno C", font=M.poppins(38, "bold"), fill=TINTA)
    filas = [("Pregunta 1", 4), ("Pregunta 2", 2), ("Pregunta 3", 5), ("Pregunta 4", 4)]
    cambio = _seg(t, 0.5, 0.58)
    for i, (n, v) in enumerate(filas):
        y = y0 + 140 + i * 92
        d.line((x0 + 30, y + 44, x1 - 30, y + 44), fill=GRIS, width=2)
        d.text((x0 + 30, y), n, font=M.inter(36, "medium"), fill=TINTA, anchor="lm")
        val = v + (1 if (i == 1 and cambio >= 1) else 0)
        caja = (x1 - 230, y - 32, x1 - 50, y + 32)
        if i == 1 and t > 0.44:
            d.rounded_rectangle(caja, 12, fill=AZUL_TINTE, outline=AZUL, width=4)
        d.text(((caja[0] + caja[2]) // 2, y), f"{val} / 5", font=M.poppins(36, "bold"),
               fill=AZUL if (i == 1 and cambio >= 1) else TINTA, anchor="mm")
    yt = y0 + 140 + 4 * 92 + 20
    d.text((x0 + 30, yt), "Nota final", font=M.poppins(40, "bold"), fill=TINTA, anchor="lm")
    d.text((x1 - 140, yt), f"{15 + (1 if cambio >= 1 else 0)} / 20", font=M.poppins(42, "bold"),
           fill=VERDE_OSC, anchor="mm")
    pc = _seg(t, 0.1, 0.42)
    sx, sy, ex, ey = 520, h - 60, x1 - 130, y0 + 140 + 92 + 10
    cx, cy = sx + (ex - sx) * pc, sy + (ey - sy) * pc
    if 0.42 < t < 0.52:
        k = _seg(t, 0.42, 0.52)
        rr = 12 + 46 * k
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=(*AZUL, int(220 * (1 - k))), width=5)
    s = 1.4
    d.polygon([(cx, cy), (cx, cy + 34 * s), (cx + 9 * s, cy + 26 * s), (cx + 16 * s, cy + 40 * s),
               (cx + 22 * s, cy + 37 * s), (cx + 15 * s, cy + 23 * s), (cx + 26 * s, cy + 22 * s)],
              fill=TINTA, outline=(255, 255, 255))
    if t > 0.7:
        d.text((x0 + 30, y0 + 92), "La nota final la decides tú", font=M.inter(30, "semibold"), fill=VERDE_OSC)
    return im


def estadisticas(t, w, h):
    """Aciertos por pregunta del grupo: la pregunta débil se ve de inmediato."""
    im, d = _lienzo(w, h)
    d.text((30, 26), "Aciertos por pregunta", font=M.poppins(38, "bold"), fill=TINTA)
    vals = [86, 78, 41, 73, 88]
    base, alto = h - 90, h - 260
    ancho = (w - 230) / len(vals)          # la esquina derecha queda libre para el Profe Eddy
    for i, v in enumerate(vals):
        p = _seg(t, 0.08 + i * 0.07, 0.4 + i * 0.07)
        bh = alto * v / 100 * p
        x, bw = 40 + i * ancho + ancho * 0.15, ancho * 0.7
        d.rounded_rectangle((x, base - bh, x + bw, base), 12, fill=NARANJA if i == 2 else AZUL)
        if p > 0.05:
            d.text((x + bw / 2, base - bh - 26), f"{int(v * p)}%", font=M.poppins(34, "bold"), fill=TINTA, anchor="mm")
        d.text((x + bw / 2, base + 36), f"P{i + 1}", font=M.inter(32, "semibold"), fill=SUAVE, anchor="mm")
    d.line((30, base, w - 30, base), fill=GRIS, width=3)
    cp = _seg(t, 0.72, 0.82)
    if cp > 0:
        a = int(255 * cp)
        x = 40 + 2 * ancho + ancho / 2
        _pastilla(d, x, 120, "P3: reforzar en clase", M.inter(32, "semibold"), NARANJA_TINTE, NARANJA_OSC, a)
        d.line((x, 152, x, 152 + (base - alto * 0.41 - 60 - 152) * cp), fill=(*NARANJA, a), width=4)
    return im


def deteccion_ia(t, w, h):
    """Un ensayo con una parte marcada y el porcentaje que parece hecho con IA."""
    im, d = _lienzo(w, h)
    x0, y0, x1 = 25, 20, 500
    _tarjeta(d, (x0, y0, x1, h - 20))
    d.text((x0 + 26, y0 + 24), "Ensayo · Alumno D", font=M.poppins(32, "bold"), fill=TINTA)
    rnd = random.Random(7)
    for i in range(10):
        y = y0 + 110 + i * 52
        lw = (x1 - x0 - 60) * rnd.uniform(0.7, 1.0)
        if 3 <= i <= 6:
            hp = _seg(t, 0.14 + (i - 3) * 0.07, 0.28 + (i - 3) * 0.07)
            if hp > 0:
                d.rounded_rectangle((x0 + 18, y - 12, x0 + 18 + (lw + 20) * hp, y + 22), 8, fill=(*NARANJA, 70))
        d.rounded_rectangle((x0 + 28, y, x0 + 28 + lw, y + 10), 5, fill=GRIS)
    cx, cy, r = 750, 230, 160
    pct = 34 * _seg(t, 0.3, 0.7)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=GRIS, width=32)
    if pct > 0:
        d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * pct / 100, fill=NARANJA, width=32)
    d.text((cx, cy), f"{int(pct)}%", font=M.poppins(90, "bold"), fill=TINTA, anchor="mm")
    d.text((cx, cy + r + 48), "parece hecho con IA", font=M.inter(32, "semibold"), fill=SUAVE, anchor="mm")
    if t > 0.8:
        d.text((cx, cy + r + 100), "Es una señal para revisar", font=M.inter(30, "semibold"), fill=AZUL, anchor="mm")
    return im


def rubrica_equipo(t, w, h):
    """La misma rúbrica se aplica a dos secciones del mismo curso."""
    im, d = _lienzo(w, h)
    rx0, rx1 = 160, 840
    _tarjeta(d, (rx0, 20, rx1, 255), relleno=AZUL_TINTE, borde=AZUL)
    d.text((rx0 + 28, 40), "Rúbrica · Matemática", font=M.poppins(34, "bold"), fill=AZUL)
    for i, (c, p) in enumerate([("Planteamiento", 2), ("Procedimiento", 2), ("Resultado", 1)]):
        y = 118 + i * 46
        d.text((rx0 + 28, y), c, font=M.inter(32, "medium"), fill=TINTA, anchor="lm")
        d.text((rx1 - 28, y), f"{p} pts", font=M.inter(32, "semibold"), fill=AZUL, anchor="rm")
    for s, nombre in enumerate(["Sección A", "Sección B"]):
        cx0 = 25 + s * 490
        d.text((cx0 + 225, 320), nombre, font=M.poppins(34, "bold"), fill=TINTA, anchor="mm")
        for k in range(3):
            x = cx0 + k * 150
            _papel(d, x, 370, 130, 190, 5, semilla=s * 5 + k)
            _check(d, x + 65, 530, 26, _seg(t, 0.56 + k * 0.08 + s * 0.04, 0.66 + k * 0.08 + s * 0.04))
        fp = _seg(t, 0.22, 0.5)
        if 0 < fp < 1:
            tx = 500 + ((cx0 + 225) - 500) * fp
            ty = 140 + (330 - 140) * fp
            d.rounded_rectangle((tx - 80, ty - 40, tx + 80, ty + 40), 12, fill=(*AZUL, int(210 * (1 - fp * 0.5))))
    if t > 0.88:
        d.text((40, h - 70), "Mismos criterios para todos", font=M.poppins(34, "semibold"), fill=VERDE_OSC)
    return im


def diapositivas(t, w, h):
    """De un tema escrito a un set de diapositivas."""
    im, d = _lienzo(w, h)
    _tarjeta(d, (25, 20, w - 25, 110))
    texto = _escribir("El ciclo del agua", _seg(t, 0.04, 0.24))
    cursor = "|" if t < 0.3 and int(t * 30) % 2 == 0 else ""
    d.text((55, 65), "Tema:", font=M.inter(34, "semibold"), fill=SUAVE, anchor="lm")
    d.text((170, 65), texto + cursor, font=M.inter(36, "medium"), fill=TINTA, anchor="lm")
    pres = _seg(t, 0.28, 0.32) * (1 - _seg(t, 0.32, 0.36))
    d.rounded_rectangle((w - 245, 32 + 3 * pres, w - 40, 98 + 3 * pres), 33, fill=VERDE_MOD)
    d.text((w - 142, 65 + 3 * pres), "Crear", font=M.inter(32, "semibold"), fill=(255, 255, 255), anchor="mm")
    titulos = ["El ciclo del agua", "Evaporación", "Condensación", "Precipitación"]
    gw, gh = (w - 25 * 2 - 24) // 2, (h - 160 - 24) // 2
    for i, tit in enumerate(titulos):
        p = _seg(t, 0.38 + i * 0.1, 0.5 + i * 0.1)
        if p <= 0:
            continue
        a = int(255 * p)
        x = 25 + (i % 2) * (gw + 24)
        y = 135 + (i // 2) * (gh + 24)
        esc = 0.85 + 0.15 * p
        cw, ch = gw * esc, gh * esc
        ox, oy = x + (gw - cw) / 2, y + (gh - ch) / 2
        d.rounded_rectangle((ox, oy, ox + cw, oy + ch), 16, fill=(255, 255, 255, a), outline=(*GRIS, a), width=3)
        d.rounded_rectangle((ox, oy, ox + cw, oy + 16), 8, fill=(*VERDE_MOD, a))
        d.text((ox + 24, oy + 40), tit, font=M.poppins(32, "bold"), fill=(*TINTA, a))
        sx, sy = ox + cw - 90, oy + ch - 80
        if i in (0, 1):
            d.ellipse((sx - 36, sy - 36, sx + 36, sy + 36), fill=(240, 160, 75, a))
        if i in (0, 2):
            d.ellipse((sx - 86, sy - 12, sx - 14, sy + 36), fill=(*GRIS, a))
            d.ellipse((sx - 56, sy - 36, sx + 12, sy + 30), fill=(*GRIS, a))
        if i == 3:
            for k in range(4):
                d.line((sx - 60 + k * 26, sy - 26, sx - 70 + k * 26, sy + 14), fill=(*AZUL, a), width=6)
        for k in range(2):
            d.rounded_rectangle((ox + 24, oy + 100 + k * 32, ox + 24 + cw * (0.45 - k * 0.12), oy + 112 + k * 32), 5,
                                fill=(*GRIS, a))
    return im


NOMBRES = {
    "lote": lote,
    "manuscrito": manuscrito,
    "semantico": semantico,
    "ajustar-nota": ajustar_nota,
    "estadisticas": estadisticas,
    "deteccion-ia": deteccion_ia,
    "rubrica-equipo": rubrica_equipo,
    "diapositivas": diapositivas,
}


def obtener(nombre: str):
    return NOMBRES.get(nombre)
