"""Client for ShellyLanMan's REST API (/api/v1) and MCP server (/mcp).

The MCP server needs its bearer token. The REST API is open unless a UI password
is set (ShellyLanMan 0.9.0+); then it needs the MCP token too, so the token goes
with every request. See COMPATIBILITY.md for what the integration relies on.
"""

from __future__ import annotations

from typing import Any

import aiohttp
from yarl import URL

from homeassistant.util.json import json_loads


# The Home Assistant app's loopback listener (app options mcp_local and
# mcp_local_port). Its address comes from ShellyLanMan's status (0.9.3+); this is
# the default for older versions.
LOCAL_URL = "http://127.0.0.1:8097"


class ShellyLanManError(Exception):
    """ShellyLanMan could not be reached or answered with an error."""


class ShellyLanManAuthError(ShellyLanManError):
    """The MCP token was refused."""


class ShellyLanManLoginRequired(ShellyLanManError):
    """ShellyLanMan has a UI password and the request had no (valid) MCP token."""


class ShellyLanManClient:
    """A small async client; one per config entry."""

    def __init__(self, session: aiohttp.ClientSession, url: str, mcp_token: str | None = None) -> None:
        self._session = session
        self.url = url.rstrip("/")
        self.mcp_token = mcp_token or None
        self._rpc_id = 0
        self._local_url: str | None = None

    def _on_this_host(self) -> bool:
        """ShellyLanMan runs as the Home Assistant app on this host (its loopback listener exists)."""
        return (URL(self.url).host or "") in ("127.0.0.1", "localhost", "::1")

    async def _request(self, method: str, path: str, json: Any = None) -> Any:
        try:
            return await self._request_at(self.url, method, path, json)
        except ShellyLanManLoginRequired:
            # The app with a UI password: its loopback listener serves these calls
            # without a token (ShellyLanMan 0.9.0, DECISIONS P15-8).
            if not self._on_this_host():
                raise
            return await self._request_at(await self.local_url(), method, path, json)

    async def local_url(self) -> str:
        """The app's loopback listener: from ShellyLanMan's status (open without login), else the default."""
        if self._local_url is None:
            url = LOCAL_URL
            try:
                async with self._session.get(f"{self.url}/api/v1/status", timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        url = (json_loads(await resp.text()) or {}).get("localUrl") or LOCAL_URL
            except (aiohttp.ClientError, TimeoutError, ValueError):
                pass
            self._local_url = str(url).rstrip("/")
        return self._local_url

    async def _request_at(self, base: str, method: str, path: str, json: Any = None) -> Any:
        headers = {"Authorization": f"Bearer {self.mcp_token}"} if self.mcp_token and base == self.url else {}
        try:
            async with self._session.request(
                method, f"{base}/api/v1{path}", json=json, headers=headers, timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                text = await resp.text()
                if resp.status == 401 and "login required" in text:
                    raise ShellyLanManLoginRequired(f"{method} {path}: ShellyLanMan asks for a password; the MCP token is needed")
                if resp.status >= 400:
                    raise ShellyLanManError(f"{method} {path}: HTTP {resp.status}: {text[:200]}")
                return json_loads(text) if text.strip() else None
        except ValueError as err:
            raise ShellyLanManError(f"{method} {path}: not JSON") from err
        except (aiohttp.ClientError, TimeoutError) as err:
            raise ShellyLanManError(f"{method} {path}: {err}") from err

    async def about(self) -> dict[str, Any]:
        """Version, instance id and more (GET /about)."""
        return await self._request("GET", "/about")

    async def devices(self) -> list[dict[str, Any]]:
        """All devices ShellyLanMan knows, with their state."""
        return await self._request("GET", "/devices") or []

    async def checklist(self) -> list[dict[str, Any]]:
        """The checklist of every device (one RPC per device: call seldom)."""
        return await self._request("GET", "/checklist") or []

    async def backups(self) -> list[dict[str, Any]]:
        """All configuration backups, newest first."""
        return await self._request("GET", "/backups") or []

    async def backup(self, device_id: str) -> list[dict[str, Any]]:
        """Back up one device's configuration; returns the result lines ({"results": [...]})."""
        answer = await self._request("POST", "/backup", {"ids": [device_id]}) or {}
        return answer.get("results") or []

    async def rescan(self) -> None:
        """Discover the devices again."""
        await self._request("POST", "/scan", {})

    async def credentials(self, device_id: str) -> dict[str, Any] | None:
        """The user and password ShellyLanMan uses for a device, or None.

        ShellyLanMan hands them out only on a trusted path (its DECISIONS P13-3):
        with the MCP token (access level "configure"), or — for the Home Assistant
        app on this host — on the app's loopback listener (LOCAL_URL). Without
        either the user types the password in Home Assistant.
        """
        path = f"/api/v1/devices/{device_id}/credentials"
        attempts: list[tuple[str, dict[str, str]]] = []
        if self.mcp_token:
            attempts.append((f"{self.url}{path}", {"Authorization": f"Bearer {self.mcp_token}"}))
        if self._on_this_host():
            attempts.append((f"{await self.local_url()}{path}", {}))
        for url, headers in attempts:
            try:
                async with self._session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        data = await resp.json(content_type=None)
                        if isinstance(data, dict) and data.get("password"):
                            return data
            except (aiohttp.ClientError, TimeoutError, ValueError):
                continue
        return None

    # ---- MCP (Streamable HTTP, JSON responses, stateless) ----

    async def mcp(self, method: str, params: dict[str, Any] | None = None) -> Any:
        """One JSON-RPC call to ShellyLanMan's MCP server."""
        self._rpc_id += 1
        body = {"jsonrpc": "2.0", "id": self._rpc_id, "method": method, "params": params or {}}
        headers = {"Accept": "application/json, text/event-stream"}
        if self.mcp_token:
            headers["Authorization"] = f"Bearer {self.mcp_token}"
        try:
            async with self._session.post(
                f"{self.url}/mcp", json=body, headers=headers, timeout=aiohttp.ClientTimeout(total=90)
            ) as resp:
                if resp.status == 401:
                    raise ShellyLanManAuthError("MCP token refused")
                if resp.status == 404:
                    raise ShellyLanManError("the MCP server is switched off in ShellyLanMan (Settings → MCP)")
                if resp.status >= 400:
                    raise ShellyLanManError(f"MCP {method}: HTTP {resp.status}")
                data = await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise ShellyLanManError(f"MCP {method}: {err}") from err
        if data.get("error"):
            raise ShellyLanManError(f"MCP {method}: {data['error'].get('message')}")
        return data.get("result")
