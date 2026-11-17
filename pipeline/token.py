"""Renueva el token de Instagram (dura 60 días) y lo guarda en los secretos del repositorio.

Requiere el secreto GH_PAT: un token personal de GitHub (fine-grained) con permiso
"Secrets: Read and write" sobre este repositorio. Sin GH_PAT solo verifica que el token siga vivo.
"""
from __future__ import annotations

import os
import subprocess

from .instagram import Instagram


def main():
    datos = Instagram().renovar_token()
    dias = int(datos.get("expires_in", 0)) // 86400
    if os.environ.get("GH_PAT") and os.environ.get("GITHUB_REPOSITORY"):
        subprocess.run(["gh", "secret", "set", "IG_ACCESS_TOKEN", "--repo", os.environ["GITHUB_REPOSITORY"]],
                       input=datos["access_token"], text=True, check=True,
                       env={**os.environ, "GH_TOKEN": os.environ["GH_PAT"]})
        print(f"Token renovado y guardado en el secreto IG_ACCESS_TOKEN (vence en {dias} días).")
    else:
        print(f"El token sigue activo (vence en {dias} días). Agrega el secreto GH_PAT para renovarlo solo.")


if __name__ == "__main__":
    main()
