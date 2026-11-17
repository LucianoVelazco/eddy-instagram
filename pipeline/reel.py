"""Montaje automático de reels 9:16 con el Profe Eddy, la demo real y subtítulos.

Tipos de escena (campo "tipo" de cada escena del guion):
  avatar  - el Profe Eddy grande habla; arriba va el texto de pantalla
  demo    - la grabación real de Eddy en un marco, con el Profe Eddy en un círculo
  texto   - tarjeta de color con un mensaje grande (datos, títulos, antes/después)
  cierre  - logo, promesa de marca y botón eddyai.lat (voz fija)
"""
from __future__ import annotations

import json
import os
import random
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from . import graficos as G
from . import marca as M
from . import voz as V

W, H, FPS = 1080, 1920, 30
ZONA_SUP, ZONA_INF = 270, 1248      # Instagram tapa el 14% superior y el 35% inferior
CAJA_DEMO = (64, 614, 1016, 1216)    # área útil de la demo dentro de la tarjeta
VERDE_CLARO = (205, 232, 220)


@dataclass
class Escena:
    tipo: str
    pantalla: str
    voz: str
    demo: str | None = None
    demo_inicio: float = 0.0
    locucion: V.Locucion | None = None
    inicio: float = 0.0
    fin: float = 0.0
    base: Image.Image | None = None
    avatar: tuple | None = None          # ("grande", x, y, ancho) | ("circulo", x, y, diametro)
    y_subtitulo: int | None = None
    demo_caja: tuple | None = None
    demo_tam: tuple | None = None
    avisos: list = field(default_factory=list)


# ---------- capas estáticas por tipo de escena ----------

def _base_avatar(e: Escena):
    im = G.fondo_claro(W, H)
    G.pegar_logo(im, 64, 292, 58)
    f = G.ajustar_fuente(e.pantalla, lambda s: M.poppins(s, "bold"), 84, 52, 940, 3, alto_max=270)
    G.dibujar_texto(im, e.pantalla, f, (70, 380, 1010, 650), M.TINTA, M.AZUL)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 1540, W, H), fill=M.AZUL_OSCURO)
    d.rectangle((0, 1540, W, 1552), fill=M.VERDE)
    e.base = im
    e.avatar = ("grande", 220, 790, 640)
    e.y_subtitulo = 714


def _base_demo(e: Escena, raiz: Path):
    im = G.fondo_claro(W, H)
    G.pegar_logo(im, 64, 292, 50)
    f = G.ajustar_fuente(e.pantalla, lambda s: M.poppins(s, "bold"), 64, 40, 940, 2, alto_max=128)
    G.dibujar_texto(im, e.pantalla, f, (70, 364, 1010, 492), M.TINTA, M.AZUL)
    G.rect_redondeado(im, (40, 590, 1040, 1240), 36, M.BLANCO, sombra=True)
    e.base = im
    e.avatar = ("circulo", 28, 1096, 250)
    e.y_subtitulo = 1170
    ruta = (raiz / e.demo) if e.demo else None
    if ruta and ruta.exists():
        ancho, alto = _dimensiones(ruta)
        cw, ch = CAJA_DEMO[2] - CAJA_DEMO[0], CAJA_DEMO[3] - CAJA_DEMO[1]
        k = min(cw / ancho, ch / alto)
        dw, dh = int(ancho * k) // 2 * 2, int(alto * k) // 2 * 2
        x = CAJA_DEMO[0] + (cw - dw) // 2
        y = CAJA_DEMO[1] + (ch - dh) // 2
        e.demo_caja, e.demo_tam = (x, y), (dw, dh)
        e.demo = str(ruta)
    else:
        e.avisos.append(f"Falta la grabación de demo '{e.demo or '(sin indicar)'}': se usó una tarjeta de texto.")
        e.demo = None
        G.rect_redondeado(im, CAJA_DEMO, 24, M.AZUL_50)
        f2 = G.ajustar_fuente(e.pantalla, lambda s: M.poppins(s, "bold"), 70, 44, 820, 4, alto_max=520)
        G.dibujar_texto(im, e.pantalla, f2, (110, 640, 970, 1190), M.AZUL_OSCURO, M.VERDE_TEXTO)


def _base_texto(e: Escena):
    im = G.degradado(W, H, M.AZUL, M.TURQUESA)
    G.pegar_logo(im, 64, 292, 58, sobre_oscuro=True)
    f = G.ajustar_fuente(e.pantalla, lambda s: M.poppins(s, "bold"), 104, 60, 920, 4, alto_max=500)
    G.dibujar_texto(im, e.pantalla, f, (80, 400, 1000, 900), M.BLANCO, VERDE_CLARO)
    e.base = im
    e.avatar = ("circulo", (W - 250) // 2, 1040, 250)
    e.y_subtitulo = 966


def _base_cierre(e: Escena):
    im = G.degradado(W, H, M.AZUL, M.TURQUESA)
    lg = G.logo(118, sobre_oscuro=True)
    im.paste(lg, ((W - lg.width) // 2, 320), lg)
    f = G.ajustar_fuente(M.PROMESA, lambda s: M.poppins(s, "bold"), 62, 44, 900, 3, alto_max=250)
    G.dibujar_texto(im, M.PROMESA, f, (90, 490, 990, 740), M.BLANCO)
    G.boton_cta(im, W // 2, 790, f"Pruébalo en {M.WEB}", 44)
    e.base = im
    e.avatar = ("grande", 250, 1000, 580)
    e.y_subtitulo = None


# ---------- utilidades ----------

def _dimensiones(ruta: Path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:stream_side_data=rotation", "-of", "json", str(ruta)],
                         capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    w, h = s["width"], s["height"]
    rot = 0
    for sd in s.get("side_data_list", []) or []:
        rot = abs(int(sd.get("rotation", 0)))
    return (h, w) if rot in (90, 270) else (w, h)


class LectorDemo:
    def __init__(self, ruta: str, inicio: float, dur: float, tam: tuple):
        self.tam = tam
        self.n = tam[0] * tam[1] * 3
        self.ultimo = None
        self.p = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-ss", f"{inicio:.2f}", "-i", ruta, "-t", f"{dur + 1:.2f}",
             "-vf", f"fps={FPS},scale={tam[0]}:{tam[1]}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.mascara = Image.new("L", tam, 0)
        ImageDraw.Draw(self.mascara).rounded_rectangle((0, 0, tam[0] - 1, tam[1] - 1), 22, fill=255)

    def siguiente(self) -> Image.Image | None:
        datos = self.p.stdout.read(self.n) if self.p.stdout else b""
        if len(datos) == self.n:
            self.ultimo = Image.frombytes("RGB", self.tam, datos)
        return self.ultimo  # si la demo es más corta, se congela el último cuadro

    def cerrar(self):
        if self.p.stdout:
            self.p.stdout.close()
        self.p.kill()


def _bloques_subtitulos(escenas: list[Escena]):
    """Agrupa palabras en bloques de hasta 4 palabras para subtítulos quemados."""
    bloques = []
    for e in escenas:
        if e.y_subtitulo is None or not e.locucion:
            continue
        pals = [(a + e.inicio, b + e.inicio, p) for a, b, p in e.locucion.palabras]
        grupo = []
        for i, (a, b, p) in enumerate(pals):
            grupo.append((a, b, p))
            corta = p.endswith((".", ",", "?", "!", ":", ";"))
            if len(grupo) >= 4 or corta or i == len(pals) - 1:
                bloques.append([grupo[0][0], grupo[-1][1], " ".join(x[2] for x in grupo), e.y_subtitulo, e.fin])
                grupo = []
    for i, bl in enumerate(bloques):  # cada bloque dura hasta que empieza el siguiente de la misma escena
        sig = bloques[i + 1][0] if i + 1 < len(bloques) else bl[4]
        bl[1] = min(bl[4], max(bl[1] + 0.25, sig if sig - bl[1] < 0.6 else bl[1] + 0.25))
    return bloques


def _imagen_subtitulo(texto: str) -> Image.Image:
    f = M.poppins(50, "semibold")
    lineas = G.envolver(texto, f, 880)
    alto_linea = 64
    w = int(max(sum(f.getlength(p) for p, _ in l) + f.getlength(" ") * (len(l) - 1) for l in lineas)) + 64
    h = alto_linea * len(lineas) + 28
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), 26, fill=(255, 255, 255, 240))
    G.dibujar_texto(im, texto, f, (32, 14, w - 32, h - 14), M.TINTA, M.AZUL, interlineado=0.86)
    return im


def _parpadeos(total: int, semilla: str):
    rnd = random.Random(semilla)
    cerrados, f = set(), int(FPS * 1.2)
    while f < total:
        cerrados.update(range(f, f + 4))
        f += int(FPS * rnd.uniform(2.6, 4.6))
    return cerrados


# ---------- render principal ----------

def renderizar(pieza: dict, contenido: dict, salida: Path, raiz: Path) -> dict:
    """Genera reel.mp4 y portada.jpg en `salida`. Devuelve metadatos y avisos."""
    salida.mkdir(parents=True, exist_ok=True)
    escenas: list[Escena] = []
    for s in contenido["escenas"]:
        tipo = s.get("tipo", "avatar")
        voz = M.CIERRE_VOZ if tipo == "cierre" and not s.get("voz") else s.get("voz", "")
        escenas.append(Escena(tipo=tipo, pantalla=s.get("pantalla", ""), voz=voz,
                              demo=s.get("demo") or (pieza.get("demo") if tipo == "demo" else None),
                              demo_inicio=float(s.get("demo_inicio", 0) or 0)))
    if not any(e.tipo == "cierre" for e in escenas):
        escenas.append(Escena(tipo="cierre", pantalla="", voz=M.CIERRE_VOZ))

    # 1) voz por escena y línea de tiempo
    pistas, t = [], 0.0
    pre, post = 0.12, 0.28
    simulada = False
    for e in escenas:
        e.locucion = V.sintetizar(e.voz)
        simulada |= e.locucion.simulada
        e.inicio = t
        pistas += [np.zeros(int(V.SR * pre), np.float32), e.locucion.audio, np.zeros(int(V.SR * post), np.float32)]
        e.locucion.palabras = [(a + pre, b + pre, p) for a, b, p in e.locucion.palabras]
        t += pre + e.locucion.duracion + post
        e.fin = t
    audio = np.concatenate(pistas)
    wav = salida / "_voz.wav"
    V.guardar_wav(audio, str(wav))
    total = int(round(t * FPS))

    # 2) capas estáticas
    for e in escenas:
        if e.tipo == "demo":
            _base_demo(e, raiz)
        elif e.tipo == "texto":
            _base_texto(e)
        elif e.tipo == "cierre":
            _base_cierre(e)
        else:
            _base_avatar(e)

    bocas = V.bocas_por_cuadro(audio, FPS)
    cerrados = _parpadeos(total, pieza.get("id", "eddy"))
    subtitulos = _bloques_subtitulos(escenas)
    cache_sub: dict[str, Image.Image] = {}

    # 3) codificación
    musica = M.RAIZ / "marca" / "musica.mp3"
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", str(wav)]
    if musica.exists():
        cmd += ["-stream_loop", "-1", "-i", str(musica), "-filter_complex",
                "[2:a]volume=0.10[m];[1:a][m]amix=inputs=2:duration=first:dropout_transition=0[a]",
                "-map", "0:v", "-map", "[a]"]
    else:
        cmd += ["-map", "0:v", "-map", "1:a"]
    destino = salida / "reel.mp4"
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart", "-shortest", str(destino)]
    enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    idx, lector = 0, None
    try:
        for f in range(total):
            tt = f / FPS
            while idx < len(escenas) - 1 and tt >= escenas[idx].fin:
                idx += 1
                if lector:
                    lector.cerrar()
                    lector = None
            e = escenas[idx]
            cuadro = e.base.copy()
            if e.tipo == "demo" and e.demo:
                if lector is None:
                    lector = LectorDemo(e.demo, e.demo_inicio, e.fin - e.inicio, e.demo_tam)
                fr = lector.siguiente()
                if fr is not None:
                    cuadro.paste(fr, e.demo_caja, lector.mascara)
            boca = bocas[f] if f < len(bocas) else 0
            ojos = f not in cerrados
            habla = boca > 0
            tipo_av, ax, ay, tam = e.avatar
            if tipo_av == "grande":
                sp = G.sprite(boca, ojos, tam)
                vaiven = int(round(3 * np.sin(2 * np.pi * 1.4 * tt))) if habla else 0
                cuadro.paste(sp, (ax, ay + vaiven), sp)
            else:
                sp = G.avatar_circulo(boca, ojos, tam)
                cuadro.paste(sp, (ax, ay), sp)
            for a, b, txt, y_sub, _ in subtitulos:
                if a <= tt < b:
                    if txt not in cache_sub:
                        cache_sub[txt] = _imagen_subtitulo(txt)
                    im = cache_sub[txt]
                    cuadro.paste(im, ((W - im.width) // 2, y_sub - im.height // 2), im)
                    break
            enc.stdin.write(cuadro.tobytes())
    finally:
        if lector:
            lector.cerrar()
        enc.stdin.close()
        enc.wait()
    wav.unlink(missing_ok=True)
    if enc.returncode != 0:
        raise RuntimeError("ffmpeg falló al codificar el reel")

    portada(contenido.get("titulo_portada") or escenas[0].pantalla, salida / "portada.jpg")
    avisos = [a for e in escenas for a in e.avisos]
    if simulada:
        avisos.append("La voz es SIMULADA (no hubo conexión con edge-tts). Vuelve a generar antes de aprobar.")
    return {"archivos": ["reel.mp4", "portada.jpg"], "duracion_s": round(t, 1), "avisos": avisos}


def portada(titulo: str, destino: Path):
    """Portada 9:16; el texto queda dentro del recorte 4:5 que muestra la cuadrícula del perfil."""
    im = G.degradado(W, H, M.AZUL, M.TURQUESA)
    G.pegar_logo(im, 90, 330, 64, sobre_oscuro=True)
    f = G.ajustar_fuente(titulo, lambda s: M.poppins(s, "bold"), 100, 60, 900, 4, alto_max=500)
    G.dibujar_texto(im, titulo, f, (90, 420, 990, 930), M.BLANCO, VERDE_CLARO, alinear="izquierda")
    sp = G.sprite(0, True, 620)
    im.paste(sp, (W - 620 + 40, 980), sp)
    im.save(destino, "JPEG", quality=92)
