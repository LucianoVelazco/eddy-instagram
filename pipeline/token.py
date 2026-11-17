"""Comprueba la conexión con Instagram: que el token y el ID de la cuenta funcionen.

El token de usuario del sistema del portfolio Eddy IA no vence, así que no hay que renovarlo.
Si alguna vez se revoca, genera otro en business.facebook.com → Usuarios del sistema → Eddy Bot.
"""
from __future__ import annotations

from .instagram import ErrorInstagram, Instagram


def main():
    ig = Instagram()
    try:
        c = ig.cuenta()
    except ErrorInstagram as e:
        raise SystemExit(f"✗ No se pudo conectar con Instagram: {e}")
    print(f"✓ Conectado a @{c.get('username')} ({c.get('name', '')}): "
          f"{c.get('followers_count', '?')} seguidores, {c.get('media_count', '?')} publicaciones.")
    try:
        lim = ig.limite()["data"][0]
        print(f"  Publicaciones por API en las últimas 24 h: {lim.get('quota_usage')} de "
              f"{lim.get('config', {}).get('quota_total', '?')}.")
    except (ErrorInstagram, KeyError, IndexError) as e:
        print(f"  (No se pudo leer el límite de publicación: {e})")


if __name__ == "__main__":
    main()
