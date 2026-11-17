"""Cliente mínimo de la API de Instagram (Graph API de Meta).

Usa un token de "usuario del sistema" del portfolio comercial Eddy IA: no vence y sirve para
publicar en la cuenta propia sin App Review (la app de Meta puede quedarse en modo desarrollo).
IG_USER_ID es el identificador de la cuenta profesional de Instagram (empieza con 1784...).
"""
from __future__ import annotations

import os
import time

import requests


class ErrorInstagram(Exception):
    pass


class Instagram:
    def __init__(self, user_id: str | None = None, token: str | None = None):
        self.user_id = user_id or os.environ["IG_USER_ID"]
        self.token = token or os.environ["IG_ACCESS_TOKEN"]
        version = (os.environ.get("IG_API_VERSION") or "").strip()
        host = (os.environ.get("IG_API_HOST") or "https://graph.facebook.com").rstrip("/")
        self.base = host + (f"/{version}" if version else "")

    def _req(self, metodo: str, ruta: str, **params):
        params["access_token"] = self.token
        url = f"{self.base}/{ruta.lstrip('/')}"
        r = requests.request(metodo, url, data=params if metodo == "POST" else None,
                             params=params if metodo == "GET" else None, timeout=120)
        try:
            datos = r.json()
        except ValueError:
            datos = {"raw": r.text[:300]}
        if r.status_code >= 400 or "error" in datos:
            err = datos.get("error", datos)
            raise ErrorInstagram(f"{r.status_code} {err.get('message', err) if isinstance(err, dict) else err}")
        return datos

    # --- publicación ---

    def _contenedor(self, **campos) -> str:
        return self._req("POST", f"{self.user_id}/media", **campos)["id"]

    def _esperar(self, contenedor: str, max_seg: int = 900):
        inicio = time.time()
        while time.time() - inicio < max_seg:
            estado = self._req("GET", contenedor, fields="status_code,status").get("status_code")
            if estado == "FINISHED":
                return
            if estado in ("ERROR", "EXPIRED"):
                raise ErrorInstagram(f"El contenedor {contenedor} quedó en {estado}")
            time.sleep(6)
        raise ErrorInstagram("Instagram tardó demasiado en procesar el archivo")

    def _publicar(self, contenedor: str) -> str:
        self._esperar(contenedor)
        return self._req("POST", f"{self.user_id}/media_publish", creation_id=contenedor)["id"]

    def reel(self, video_url: str, texto: str, portada_url: str | None = None) -> str:
        campos = dict(media_type="REELS", video_url=video_url, caption=texto, share_to_feed="true")
        if portada_url:
            campos["cover_url"] = portada_url
        return self._publicar(self._contenedor(**campos))

    def imagen(self, image_url: str, texto: str) -> str:
        return self._publicar(self._contenedor(image_url=image_url, caption=texto))

    def story(self, url: str, es_video: bool = False) -> str:
        campos = dict(media_type="STORIES")
        campos["video_url" if es_video else "image_url"] = url
        return self._publicar(self._contenedor(**campos))

    def carrusel(self, image_urls: list[str], texto: str) -> str:
        hijos = []
        for u in image_urls:
            hijos.append(self._contenedor(image_url=u, is_carousel_item="true"))
        for h in hijos:
            self._esperar(h, 300)
        return self._publicar(self._contenedor(media_type="CAROUSEL", children=",".join(hijos), caption=texto))

    def enlace(self, media_id: str) -> str:
        return self._req("GET", media_id, fields="permalink").get("permalink", "")

    # --- métricas y token ---

    def metricas(self, media_id: str, nombres: list[str]) -> dict:
        try:
            datos = self._req("GET", f"{media_id}/insights", metric=",".join(nombres))["data"]
            return {d["name"]: (d.get("values") or [{}])[0].get("value", d.get("total_value", {}).get("value"))
                    for d in datos}
        except ErrorInstagram:
            out = {}
            for n in nombres:  # si alguna métrica no aplica a este tipo de publicación, se pide una por una
                try:
                    d = self._req("GET", f"{media_id}/insights", metric=n)["data"][0]
                    out[n] = (d.get("values") or [{}])[0].get("value")
                except ErrorInstagram:
                    out[n] = None
            return out

    def cuenta(self) -> dict:
        """Datos básicos de la cuenta: sirve para comprobar que el token y el ID funcionan."""
        return self._req("GET", self.user_id, fields="username,name,followers_count,media_count")

    def limite(self) -> dict:
        return self._req("GET", f"{self.user_id}/content_publishing_limit", fields="config,quota_usage")
