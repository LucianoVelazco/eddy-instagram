"""Voz gratuita con edge-tts (voces neuronales de Microsoft, español de Perú).

Devuelve el audio como arreglo numpy mono a 24 kHz y los tiempos de cada palabra
para los subtítulos. Si edge-tts no está disponible (sin internet), genera una
pista de silencio con la duración estimada y marca la voz como simulada, para
que el resto del pipeline pueda probarse igual.
"""
from __future__ import annotations

import asyncio
import os
import subprocess
import tempfile
from dataclasses import dataclass, field

import numpy as np

SR = 24000
VOZ = os.environ.get("EDDY_VOZ") or "es-PE-AlexNeural"      # alternativa: es-PE-CamilaNeural
VELOCIDAD = os.environ.get("EDDY_VOZ_VELOCIDAD") or "+8%"


@dataclass
class Locucion:
    audio: np.ndarray                 # float32 mono, SR Hz
    palabras: list = field(default_factory=list)   # [(inicio_s, fin_s, palabra)]
    simulada: bool = False

    @property
    def duracion(self) -> float:
        return len(self.audio) / SR


def _decodificar(ruta: str) -> np.ndarray:
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", ruta, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
        check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


async def _edge(texto: str, ruta: str):
    import edge_tts
    try:
        com = edge_tts.Communicate(texto, VOZ, rate=VELOCIDAD, boundary="WordBoundary")
    except TypeError:  # versiones antiguas sin el parámetro boundary
        com = edge_tts.Communicate(texto, VOZ, rate=VELOCIDAD)
    palabras = []
    with open(ruta, "wb") as f:
        async for trozo in com.stream():
            if trozo["type"] == "audio":
                f.write(trozo["data"])
            elif trozo["type"] == "WordBoundary":
                ini = trozo["offset"] / 1e7
                palabras.append((ini, ini + trozo["duration"] / 1e7, trozo["text"]))
    return palabras


def _repartir(texto: str, dur: float, inicio: float = 0.0):
    pals = texto.split()
    if not pals:
        return []
    pesos = np.array([max(2, len(p)) for p in pals], dtype=float)
    cortes = np.concatenate([[0], np.cumsum(pesos)]) / pesos.sum() * dur
    return [(inicio + cortes[i], inicio + cortes[i + 1], p) for i, p in enumerate(pals)]


def sintetizar(texto: str) -> Locucion:
    texto = " ".join(texto.split())
    if not texto:
        return Locucion(np.zeros(int(SR * 0.4), dtype=np.float32))
    if os.environ.get("EDDY_VOZ_SIMULADA") != "1":
        try:
            with tempfile.TemporaryDirectory() as tmp:
                ruta = os.path.join(tmp, "voz.mp3")
                palabras = asyncio.run(_edge(texto, ruta))
                audio = _decodificar(ruta)
            if len(audio) > SR * 0.3:
                if not palabras:
                    palabras = _repartir(texto, len(audio) / SR)
                return Locucion(audio, palabras)
        except Exception as e:  # sin red o servicio caído
            print(f"  [voz] edge-tts no disponible ({type(e).__name__}: {e}); uso voz simulada")
    # Voz simulada: ~2.6 palabras por segundo, con un tono bajo modulado para probar el lip-sync
    dur = max(1.2, len(texto.split()) / 2.6)
    t = np.arange(int(SR * dur)) / SR
    env = (0.5 + 0.5 * np.sin(2 * np.pi * 3.1 * t)) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * t))
    audio = (0.08 * env * np.sin(2 * np.pi * 180 * t)).astype(np.float32)
    return Locucion(audio, _repartir(texto, dur), simulada=True)


def guardar_wav(audio: np.ndarray, ruta: str):
    import wave
    pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    with wave.open(ruta, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def bocas_por_cuadro(audio: np.ndarray, fps: int) -> list[int]:
    """Lip-sync por amplitud: 0 cerrada, 1 media, 2 abierta para cada cuadro de video."""
    paso = SR / fps
    n = int(len(audio) / paso) + 1
    rms = np.zeros(n)
    for i in range(n):
        seg = audio[int(i * paso): int((i + 1) * paso)]
        rms[i] = np.sqrt(np.mean(seg ** 2)) if len(seg) else 0.0
    ref = np.percentile(rms[rms > 1e-4], 90) if np.any(rms > 1e-4) else 1.0
    nivel = rms / (ref + 1e-9)
    estados = np.where(nivel > 0.55, 2, np.where(nivel > 0.18, 1, 0))
    # suavizado: evita parpadeos de un solo cuadro
    for i in range(1, n - 1):
        if estados[i] != estados[i - 1] and estados[i] != estados[i + 1]:
            estados[i] = estados[i - 1]
    return estados.tolist()
