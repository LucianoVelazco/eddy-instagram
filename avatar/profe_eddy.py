"""Profe Eddy: personaje original de la marca Eddy IA.

Genera el SVG del personaje con variantes de boca (0 cerrada, 1 media, 2 abierta)
y de ojos (abiertos / cerrados) y los renderiza a PNG transparentes.

Uso:
    python avatar/profe_eddy.py            # genera avatar/sprites/*.png
"""
from __future__ import annotations

import io
from pathlib import Path

SKIN = "#C68B59"
SKIN_DARK = "#A86F43"
HAIR = "#2B2118"
INK = "#1F2937"
BLUE = "#2F68B0"
BLUE_DARK = "#275794"
GREEN = "#58B389"
ORANGE = "#F0A04B"
MOUTH = "#5B2A1E"
TONGUE = "#E06A6A"

W, H = 600, 720


def _mouth(state: int) -> str:
    if state == 0:
        return (f"<path d='M262 402 Q300 430 338 402' stroke='{MOUTH}' stroke-width='8' "
                "fill='none' stroke-linecap='round'/>")
    if state == 1:
        shape = "M266 398 Q300 450 334 398 Q300 410 266 398 Z"
        return (f"<clipPath id='m1'><path d='{shape}'/></clipPath>"
                f"<path d='{shape}' fill='{MOUTH}'/>"
                f"<ellipse cx='300' cy='424' rx='16' ry='8' fill='{TONGUE}' clip-path='url(#m1)'/>")
    shape = "M258 394 Q300 482 342 394 Q300 406 258 394 Z"
    return (f"<clipPath id='m2'><path d='{shape}'/></clipPath>"
            f"<path d='{shape}' fill='{MOUTH}'/>"
            f"<g clip-path='url(#m2)'><path d='M258 396 Q300 410 342 396 L342 410 Q300 420 258 410 Z' fill='#FFFFFF'/>"
            f"<ellipse cx='300' cy='436' rx='24' ry='10' fill='{TONGUE}'/></g>")


def _eyes(open_: bool) -> str:
    if open_:
        return (f"<circle cx='235' cy='305' r='14' fill='{INK}'/>"
                f"<circle cx='365' cy='305' r='14' fill='{INK}'/>"
                "<circle cx='240' cy='299' r='4.5' fill='#FFFFFF'/>"
                "<circle cx='370' cy='299' r='4.5' fill='#FFFFFF'/>")
    return (f"<path d='M219 307 Q235 318 251 307' stroke='{INK}' stroke-width='6' fill='none' stroke-linecap='round'/>"
            f"<path d='M349 307 Q365 318 381 307' stroke='{INK}' stroke-width='6' fill='none' stroke-linecap='round'/>")


def svg(mouth: int = 0, eyes_open: bool = True) -> str:
    return f"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}'>
  <!-- camisa y corbata -->
  <path d='M228 512 L300 650 L372 512 Z' fill='#FFFFFF'/>
  <path d='M291 572 L309 572 L318 600 L300 700 L282 600 Z' fill='{GREEN}'/>
  <path d='M286 556 L314 556 L309 574 L291 574 Z' fill='#479571'/>
  <!-- suéter -->
  <path d='M30 720 C34 612 116 548 226 512 L300 652 L374 512 C484 548 566 612 570 720 Z' fill='{BLUE}'/>
  <path d='M226 512 L300 652 L374 512 L362 508 L300 624 L238 508 Z' fill='{BLUE_DARK}'/>
  <!-- cuello de camisa -->
  <path d='M236 506 L300 566 L262 596 L222 530 Z' fill='#FFFFFF' stroke='#E2E8F0' stroke-width='3'/>
  <path d='M364 506 L300 566 L338 596 L378 530 Z' fill='#FFFFFF' stroke='#E2E8F0' stroke-width='3'/>
  <!-- pin verde -->
  <circle cx='452' cy='612' r='18' fill='{GREEN}'/>
  <circle cx='452' cy='612' r='8' fill='#FFFFFF'/>
  <!-- cuello -->
  <rect x='252' y='420' width='96' height='110' rx='34' fill='{SKIN}'/>
  <path d='M252 460 Q300 498 348 460 L348 440 L252 440 Z' fill='{SKIN_DARK}' opacity='0.55'/>
  <!-- orejas -->
  <ellipse cx='157' cy='318' rx='24' ry='36' fill='{SKIN}'/>
  <ellipse cx='443' cy='318' rx='24' ry='36' fill='{SKIN}'/>
  <ellipse cx='160' cy='320' rx='10' ry='18' fill='{SKIN_DARK}' opacity='0.5'/>
  <ellipse cx='440' cy='320' rx='10' ry='18' fill='{SKIN_DARK}' opacity='0.5'/>
  <!-- lápiz detrás de la oreja -->
  <g transform='rotate(38 455 245)'>
    <rect x='430' y='160' width='26' height='120' rx='4' fill='{ORANGE}'/>
    <rect x='430' y='160' width='26' height='18' rx='4' fill='#E2E8F0'/>
    <path d='M430 280 L456 280 L443 312 Z' fill='#F6D7A7'/>
    <path d='M438 300 L448 300 L443 312 Z' fill='{INK}'/>
  </g>
  <!-- cabeza -->
  <ellipse cx='300' cy='296' rx='146' ry='164' fill='{SKIN}'/>
  <!-- cabello -->
  <path d='M150 290 C138 168 218 108 306 106 C404 106 466 170 450 292 C440 236 418 206 386 192 C346 222 270 232 214 214 C186 232 162 258 150 290 Z' fill='{HAIR}'/>
  <path d='M214 214 C262 196 312 168 344 134 C330 176 300 206 262 222 Z' fill='#3A2C20'/>
  <!-- cejas -->
  <rect x='206' y='248' width='62' height='12' rx='6' fill='{HAIR}' transform='rotate(-6 237 254)'/>
  <rect x='332' y='248' width='62' height='12' rx='6' fill='{HAIR}' transform='rotate(6 363 254)'/>
  <!-- mejillas -->
  <circle cx='212' cy='372' r='24' fill='#E07A5F' opacity='0.22'/>
  <circle cx='388' cy='372' r='24' fill='#E07A5F' opacity='0.22'/>
  <!-- ojos -->
  {_eyes(eyes_open)}
  <!-- lentes -->
  <rect x='183' y='266' width='104' height='80' rx='28' fill='#FFFFFF' fill-opacity='0.12' stroke='{INK}' stroke-width='7'/>
  <rect x='313' y='266' width='104' height='80' rx='28' fill='#FFFFFF' fill-opacity='0.12' stroke='{INK}' stroke-width='7'/>
  <path d='M287 298 Q300 286 313 298' stroke='{INK}' stroke-width='7' fill='none'/>
  <path d='M183 296 L162 290' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>
  <path d='M417 296 L438 290' stroke='{INK}' stroke-width='7' stroke-linecap='round'/>
  <!-- nariz -->
  <path d='M302 318 Q288 356 298 366 Q308 372 318 362' stroke='{SKIN_DARK}' stroke-width='6' fill='none' stroke-linecap='round'/>
  <!-- boca -->
  {_mouth(mouth)}
</svg>"""


def render_png(mouth: int, eyes_open: bool, width: int = 900) -> bytes:
    import cairosvg
    return cairosvg.svg2png(bytestring=svg(mouth, eyes_open).encode(), output_width=width,
                            output_height=int(width * H / W))


def build_sprites(out_dir: Path, width: int = 900) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for m in (0, 1, 2):
        for e, tag in ((True, "abiertos"), (False, "cerrados")):
            (out_dir / f"boca{m}_ojos_{tag}.png").write_bytes(render_png(m, e, width))
    (out_dir / "profe_eddy.svg").write_text(svg(0, True), encoding="utf-8")


if __name__ == "__main__":
    build_sprites(Path(__file__).parent / "sprites")
    print("Sprites generados en avatar/sprites/")
