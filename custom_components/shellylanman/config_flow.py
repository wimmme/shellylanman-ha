"""Set-up: by hand (URL, optional MCP token) or from the app's discovery."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_URL
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.service_info.hassio import HassioServiceInfo

from .api import ShellyLanManAuthError, ShellyLanManClient, ShellyLanManError
from .const import CONF_MCP_TOKEN, DOMAIN, vol


def _schema(url: str = "", token: str = "") -> Any:
    return vol.Schema({
        vol.Required(CONF_URL, default=url): str,
        vol.Optional(CONF_MCP_TOKEN, description={"suggested_value": token}): str,
    })


class ShellyLanManConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow of ShellyLanMan."""

    VERSION = 1

    def __init__(self) -> None:
        self._url = ""

    async def _check(self, url: str, token: str | None) -> tuple[dict[str, Any] | None, str | None]:
        """Read ShellyLanMan's about (and, with a token, its MCP tools); return (about, error key)."""
        client = ShellyLanManClient(async_get_clientsession(self.hass), url, token)
        try:
            about = await client.about()
            if token:
                await client.mcp("tools/list")
        except ShellyLanManAuthError:
            return None, "invalid_token"
        except ShellyLanManError:
            return None, "cannot_connect"
        if not about.get("instanceId"):
            return None, "too_old"
        return about, None

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Set up by hand."""
        errors: dict[str, str] = {}
        if user_input is not None:
            url = user_input[CONF_URL].strip().rstrip("/")
            token = (user_input.get(CONF_MCP_TOKEN) or "").strip() or None
            about, error = await self._check(url, token)
            if about:
                await self.async_set_unique_id(about["instanceId"])
                self._abort_if_unique_id_configured(updates={CONF_URL: url})
                data = {CONF_URL: url}
                if token:
                    data[CONF_MCP_TOKEN] = token
                return self.async_create_entry(title="ShellyLanMan", data=data)
            errors["base"] = error or "unknown"
        url = user_input[CONF_URL] if user_input else "http://"
        token = user_input.get(CONF_MCP_TOKEN, "") if user_input else ""
        return self.async_show_form(step_id="user", data_schema=_schema(url, token), errors=errors)

    async def async_step_hassio(self, discovery_info: HassioServiceInfo) -> ConfigFlowResult:
        """ShellyLanMan runs as a Home Assistant app and announced itself."""
        url = str(discovery_info.config.get("url", "")).rstrip("/")
        about, error = await self._check(url, None)
        if not about:
            return self.async_abort(reason=error or "cannot_connect")
        await self.async_set_unique_id(about["instanceId"])
        self._abort_if_unique_id_configured(updates={CONF_URL: url})  # e.g. after a port change
        self._url = url
        return await self.async_step_hassio_confirm()

    async def async_step_hassio_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Confirm the discovered ShellyLanMan."""
        if user_input is not None:
            return self.async_create_entry(title="ShellyLanMan", data={CONF_URL: self._url})
        self._set_confirm_only()
        return self.async_show_form(step_id="hassio_confirm", description_placeholders={"url": self._url})

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Change the URL or the MCP token."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            url = user_input[CONF_URL].strip().rstrip("/")
            token = (user_input.get(CONF_MCP_TOKEN) or "").strip() or None
            about, error = await self._check(url, token)
            if about:
                await self.async_set_unique_id(about["instanceId"])
                self._abort_if_unique_id_mismatch(reason="wrong_instance")
                data = {CONF_URL: url}
                if token:
                    data[CONF_MCP_TOKEN] = token
                return self.async_update_reload_and_abort(entry, data=data)
            errors["base"] = error or "unknown"
        return self.async_show_form(step_id="reconfigure", data_schema=_schema(entry.data[CONF_URL], entry.data.get(CONF_MCP_TOKEN, "")), errors=errors)
