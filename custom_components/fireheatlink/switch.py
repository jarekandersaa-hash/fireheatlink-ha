from __future__ import annotations

from homeassistant.components.switch import SwitchEntity

from . import BoilerEntity
from .const import DOMAIN

# klucz, pole statusu, komenda wlaczenia, komenda wylaczenia
ITEMS = (
    ("running", "running", "START", "STOP"),
    ("manual", "manualMode", "MANUAL", "AUTO"),
    ("room_control", "roomTempControl", "SET_ROOM_CTRL:1", "SET_ROOM_CTRL:0"),
)


async def async_setup_entry(hass, entry, add):
    c = hass.data[DOMAIN][entry.entry_id]
    add(BoilerSwitch(c, *i) for i in ITEMS)


class BoilerSwitch(BoilerEntity, SwitchEntity):
    def __init__(self, coordinator, key, field, on_cmd, off_cmd) -> None:
        super().__init__(coordinator, key)
        self._field, self._on, self._off = field, on_cmd, off_cmd

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get(self._field))

    async def async_turn_on(self, **kw) -> None:
        await self.coordinator.send(self._on)

    async def async_turn_off(self, **kw) -> None:
        await self.coordinator.send(self._off)
