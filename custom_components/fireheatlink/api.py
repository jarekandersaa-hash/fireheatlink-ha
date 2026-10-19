"""Lokalne API sterownika (HTTP w sieci domowej, bez serwera MQTT)."""
from __future__ import annotations

import asyncio
import hashlib
from typing import Any

import aiohttp

TIMEOUT = aiohttp.ClientTimeout(total=8)


class BoilerError(Exception):
    """Sterownik nie odpowiada lub zwrocil bledne dane."""


class BoilerApi:
    def __init__(self, session: aiohttp.ClientSession, host: str) -> None:
        self._s = session
        self.host = host

    @property
    def base(self) -> str:
        return f"http://{self.host}"

    async def status(self) -> dict[str, Any]:
        try:
            async with self._s.get(f"{self.base}/api/status", timeout=TIMEOUT) as r:
                r.raise_for_status()
                data = await r.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as e:
            raise BoilerError(str(e)) from e
        if not isinstance(data, dict) or "tempPiec" not in data:
            raise BoilerError("to nie jest sterownik pieca")
        return data

    async def command(self, cmd: str) -> None:
        """Te same komendy co w aplikacji (START, STOP, SET_PIEC:65 ...)."""
        try:
            async with self._s.get(f"{self.base}/api/cmd", params={"c": cmd}, timeout=TIMEOUT) as r:
                r.raise_for_status()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            raise BoilerError(str(e)) from e


def device_uid(status: dict[str, Any], host: str) -> str:
    """Stabilny identyfikator z tajnego tematu ntfy (haszowany, zeby sekret nie trafial do HA)."""
    ntfy = status.get("ntfy") or ""
    if len(ntfy) >= 16:
        return hashlib.sha1(ntfy.encode()).hexdigest()[:12]
    return host
