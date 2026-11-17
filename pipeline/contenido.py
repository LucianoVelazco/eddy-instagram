"""Guiones y copies de cada pieza.

Orden de prioridad:
  1. contenido/<id>.json escrito o editado por el equipo (los 16 del primer mes ya vienen listos)
  2. Gemini (API gratuita de Google AI Studio) si existe la variable GEMINI_API_KEY;
     el resultado se guarda en contenido/<id>.json para revisarlo en el PR
  3. Una plantilla básica, marcada con aviso para que alguien la reescriba
"""
from __future__ import annotations

import json
import os
import re

import requests

from . import marca as M
from .calendario import FORMATOS_REEL

CARPETA = M.RAIZ / "contenido"

REGLAS_MARCA = """Eres el redactor de Eddy IA (eddyai.lat), plataforma de Bable (Perú) que ayuda a docentes
de secundaria y universidad a corregir exámenes con inteligencia artificial.
Voz: colega docente que sabe de tecnología. Tuteo, frases cortas, verbos directos, español latino neutro
con cercanía peruana. Nada de jerga técnica ni promesas infladas. Máximo 2 emoji en el copy, ninguno en pantalla.
Datos que SÍ puedes usar (no inventes otros, ni cifras, ni testimonios, ni funciones):
- Ahorra HASTA un 90% del tiempo de evaluación (siempre con "hasta").
- El docente define los criterios (clave de respuesta o rúbrica) y decide la nota final; Eddy da un resultado preliminar.
- Análisis semántico: evalúa el sentido de la respuesta, no solo palabras exactas.
- Lee escritura manuscrita legible; corrige textos, cálculos y gráficos; preguntas abiertas y cerradas.
- Sube varias pruebas a la vez: escaneo, foto o archivo.
- Retroalimentación inmediata y personalizada; resultados por estudiante y estadísticas por grupo.
- Detección del porcentaje de trabajo hecho con IA: es una señal para revisar, no una prueba.
- Creación de diapositivas. Tutoriales de uso. Funciona con créditos.
- Trabaja con docentes, colegios y universidades (evaluación uniforme entre docentes y cursos).
Promesa de marca: "Tu tiempo es para enseñar, no para corregir exámenes."
Para resaltar palabras clave en textos de pantalla, enciérralas entre asteriscos: *así*."""

ESQUEMAS = {
    "reel": """Devuelve SOLO un JSON con esta forma:
{"titulo_portada": "máx. 8 palabras",
 "escenas": [
   {"tipo": "avatar", "pantalla": "hook, máx. 7 palabras", "voz": "lo que dice el Profe Eddy, máx. 22 palabras"},
   {"tipo": "demo", "pantalla": "máx. 7 palabras", "voz": "narración de la demo, máx. 30 palabras"},
   {"tipo": "avatar" o "texto", "pantalla": "beneficio, máx. 7 palabras", "voz": "máx. 20 palabras"},
   {"tipo": "cierre"}
 ],
 "copy": "gancho de máx. 125 caracteres en la primera línea, luego 2 a 4 líneas y un solo CTA",
 "hashtags": ["#EddyIA", "... 3 a 5 en total"],
 "hooks_alternativos": ["3 hooks distintos para probar"]}
Duración total hablada: 20 a 35 segundos. Los números en "voz" se escriben en letras (noventa por ciento).""",
    "carrusel": """Devuelve SOLO un JSON con esta forma:
{"laminas": [
   {"sobretitulo": "pilar en 2-3 palabras", "titulo": "portada, máx. 9 palabras", "texto": "subtítulo, máx. 14 palabras"},
   {"titulo": "máx. 8 palabras", "texto": "máx. 35 palabras"}
   ... de 4 a 6 láminas interiores en total
 ],
 "cta": {"titulo": "máx. 6 palabras", "texto": "invitación a guardar o compartir, máx. 12 palabras"},
 "copy": "gancho de máx. 125 caracteres, luego 2 a 4 líneas y un solo CTA",
 "hashtags": ["#EddyIA", "... 3 a 5 en total"]}""",
    "post": """Devuelve SOLO un JSON con esta forma:
{"frase": "máx. 12 palabras, con 1 o 2 palabras *resaltadas*",
 "subtitulo": "máx. 14 palabras",
 "copy": "gancho de máx. 125 caracteres, luego 2 a 3 líneas y un solo CTA",
 "hashtags": ["#EddyIA", "... 3 a 5 en total"]}""",
}
ESQUEMAS["story"] = ESQUEMAS["post"]

DESCRIPCION_FORMATO = {
    "reel_avatar": "Reel 'Eddy explica': el Profe Eddy abre con el hook, luego la demo real, luego el beneficio.",
    "reel_demo": "Reel 'Míralo corregir': casi todo es la demo real en pantalla, narrada; el Profe Eddy solo abre.",
    "reel_faq": "Reel 'Pregunta frecuente': la pregunta en pantalla, el Profe Eddy responde, la demo lo prueba.",
    "reel_antes_despues": "Reel 'Antes y después': escena de texto con el antes (noches corrigiendo), luego la demo, luego el después.",
    "carrusel": "Carrusel educativo de 1080x1350 que la gente guarda.",
    "post": "Post de una imagen con una frase o dato.",
    "story": "Story con una pregunta para la comunidad docente.",
}


def _tipo(formato: str) -> str:
    return "reel" if formato in FORMATOS_REEL else formato


def _gemini(pieza: dict) -> dict:
    clave = os.environ["GEMINI_API_KEY"]
    modelo = os.environ.get("GEMINI_MODEL") or "gemini-flash-latest"
    prompt = f"""{REGLAS_MARCA}

Pieza a escribir:
- Formato: {pieza['formato']} — {DESCRIPCION_FORMATO.get(pieza['formato'], '')}
- Pilar: {pieza['pilar']}
- Bondad que debe probar: {pieza['bondad']}
- Título de trabajo: {pieza['titulo']}
- Toma de demo disponible: {pieza.get('demo') or 'ninguna'}

{ESQUEMAS[_tipo(pieza['formato'])]}"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    r = requests.post(url, headers={"x-goog-api-key": clave, "Content-Type": "application/json"},
                      json={"contents": [{"parts": [{"text": prompt}]}],
                            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.8}},
                      timeout=90)
    r.raise_for_status()
    texto = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    texto = re.sub(r"^```(json)?|```$", "", texto.strip()).strip()
    return json.loads(texto)


def _plantilla(pieza: dict) -> dict:
    titulo = pieza["titulo"]
    base = {"copy": f"{titulo}\n\nEddy IA corrige contigo y tú decides la nota final.\n\n"
                    f"Pruébalo en {M.WEB} (enlace en la bio).",
            "hashtags": M.HASHTAGS_BASE + ["#docentesperú"]}
    t = _tipo(pieza["formato"])
    if t == "reel":
        base.update({"titulo_portada": titulo, "escenas": [
            {"tipo": "avatar", "pantalla": titulo, "voz": titulo},
            {"tipo": "demo", "pantalla": pieza["bondad"], "voz": f"Mira cómo funciona: {pieza['bondad']}."},
            {"tipo": "cierre"}]})
    elif t == "carrusel":
        base.update({"laminas": [{"titulo": titulo, "texto": pieza["bondad"]},
                                 {"titulo": pieza["bondad"], "texto": "Escribe aquí el contenido."}]})
    else:
        base.update({"frase": titulo, "subtitulo": pieza["bondad"]})
    return base


def cargar(pieza: dict) -> tuple[dict, str, list[str]]:
    ruta = CARPETA / f"{pieza['id']}.json"
    if ruta.exists():
        return json.loads(ruta.read_text(encoding="utf-8")), "archivo", []
    avisos = []
    if os.environ.get("GEMINI_API_KEY"):
        try:
            c = _gemini(pieza)
            CARPETA.mkdir(exist_ok=True)
            ruta.write_text(json.dumps(c, ensure_ascii=False, indent=2), encoding="utf-8")
            return c, "gemini", ["Guion escrito por Gemini: revísalo con cuidado antes de aprobar."]
        except Exception as e:
            avisos.append(f"Gemini falló ({type(e).__name__}: {e}); se usó una plantilla básica.")
    else:
        avisos.append("No hay guion en contenido/ ni GEMINI_API_KEY: se usó una plantilla básica. Reescríbela.")
    return _plantilla(pieza), "plantilla", avisos


_PROHIBIDAS = ["garantizad", "revoluciona", "100%", "sin errores", "corrige solo", "califica solo"]
_EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")


def revisar(pieza: dict, c: dict) -> list[str]:
    """Reglas de la línea de marca que se pueden verificar de forma automática."""
    avisos = []
    textos = json.dumps(c, ensure_ascii=False)
    if re.search(r"90 ?%|noventa por ciento", textos, re.I):
        for m in re.finditer(r"(.{0,30})(90 ?%|noventa por ciento)", textos, re.I):
            if "hasta" not in m.group(1).lower():
                avisos.append("Aparece '90%' sin 'hasta' delante.")
                break
    for p in _PROHIBIDAS:
        if p in textos.lower():
            avisos.append(f"Frase fuera de la línea de marca: '{p}'.")
    copy = c.get("copy", "")
    if copy and len(copy.splitlines()[0]) > 125:
        avisos.append("La primera línea del copy pasa de 125 caracteres (se corta antes del 'más').")
    if len(copy) + len(" ".join(c.get("hashtags", []))) > 2150:
        avisos.append("El copy con hashtags se acerca al límite de 2200 caracteres.")
    if len(_EMOJI.findall(copy)) > 2:
        avisos.append("El copy tiene más de 2 emoji.")
    if not 3 <= len(c.get("hashtags", [])) <= 5:
        avisos.append("Usa de 3 a 5 hashtags.")
    for e in c.get("escenas", []):
        if len(e.get("pantalla", "").split()) > 9:
            avisos.append(f"Texto de pantalla largo (>9 palabras): '{e['pantalla']}'.")
        if len(e.get("voz", "").split()) > 40:
            avisos.append("Una escena tiene más de 40 palabras de voz; el reel se alarga.")
    if pieza["formato"] in FORMATOS_REEL and not any(e.get("tipo") == "demo" for e in c.get("escenas", [])):
        avisos.append("El reel no tiene escena de demo: la regla de marca pide probar la bondad en pantalla.")
    return avisos


def texto_publicacion(c: dict) -> str:
    return (c.get("copy", "").strip() + "\n\n" + " ".join(c.get("hashtags", []))).strip()
