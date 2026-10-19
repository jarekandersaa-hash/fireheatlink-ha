"""Sterownik pieca CO: integracja przez lokalne API (HTTP w LAN, bez brokera MQTT)."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator, UpdateFailed

from .api import BoilerApi, BoilerError
from .const import DEFAULT_NAME, DOMAIN, SCAN_INTERVAL_S

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.SWITCH, Platform.NUMBER]


class BoilerCoordinator(DataUpdateCoordinator[dict]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=SCAN_INTERVAL_S))
        self.api = BoilerApi(async_get_clientsession(hass), entry.data[CONF_HOST])
        self.uid = entry.unique_id or entry.entry_id

    async def _async_update_data(self) -> dict:
        try:
            return await self.api.status()
        except BoilerError as e:
            raise UpdateFailed(str(e)) from e

    async def send(self, cmd: str) -> None:
        await self.api.command(cmd)
        await self.async_request_refresh()


class BoilerEntity(CoordinatorEntity[BoilerCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: BoilerCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.uid}_{key}"
        self._attr_translation_key = key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.uid)},
            name=DEFAULT_NAME,
            manufacturer="FireHeatLink",
            model="Boiler Controller",
            configuration_url=f"http://{coordinator.api.host}",
        )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coord = BoilerCoordinator(hass, entry)
    await coord.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coord
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return ok
