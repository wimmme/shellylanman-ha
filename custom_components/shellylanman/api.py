"""Client for ShellyLanMan's REST API (/api/v1) and MCP server (/mcp).

The REST API has no login on the LAN (ShellyLanMan's design); the MCP server
needs its bearer token. See COMPATIBILITY.md for what the integration relies on.
"""

from __future__ import annotations

from typing import Any

import aiohttp

from homeassistant.util.json import json_loads


class ShellyLanManError(Exception):
    """ShellyLanMan could not be reached or answered with an error."""


class ShellyLanManAuthError(ShellyLanManError):
    """The MCP token was refused."""


class ShellyLanManClient:
    """A small async client; one per config entry."""

    def __init__(self, session: aiohttp.ClientSession, url: str, mcp_token: str | None = None) -> None:
        self._session = session
        self.url = url.rstrip("/")
        self.mcp_token = mcp_token or None
        self._rpc_id = 0

    async def _request(self, method: str, path: str, json: Any = None) -> Any:
        try:
            async with self._session.request(
                method, f"{self.url}/api/v1{path}", json=json, timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                text = await resp.text()
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
