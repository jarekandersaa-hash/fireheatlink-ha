"""Konfiguracja z interfejsu: automatyczne wykrycie (mDNS) albo reczny adres."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import BoilerApi, BoilerError, device_uid
from .const import DEFAULT_NAME, DOMAIN


class FireHeatLinkFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    _host: str = ""

    async def _probe(self, host: str) -> str:
        """Zwraca unikalny id sterownika albo rzuca BoilerError."""
        st = await BoilerApi(async_get_clientsession(self.hass), host).status()
        return device_uid(st, host)

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip().removeprefix("http://").strip("/")
            try:
                uid = await self._probe(host)
            except BoilerError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(uid)
                self._abort_if_unique_id_configured(updates={CONF_HOST: host})
                return self.async_create_entry(title=DEFAULT_NAME, data={CONF_HOST: host})
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_HOST, default="boiler.local"): str}),
            errors=errors,
        )

    async def async_step_zeroconf(self, discovery_info):
        host = str(discovery_info.ip_address)
        try:
            uid = await self._probe(host)
        except BoilerError:
            return self.async_abort(reason="not_boiler")
        await self.async_set_unique_id(uid)
        self._abort_if_unique_id_configured(updates={CONF_HOST: host})
        self._host = host
        self.context["title_placeholders"] = {"name": DEFAULT_NAME}
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(title=DEFAULT_NAME, data={CONF_HOST: self._host})
        return self.async_show_form(step_id="confirm", description_placeholders={"host": self._host})
