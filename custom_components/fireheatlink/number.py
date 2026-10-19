from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import UnitOfTemperature

from . import BoilerEntity
from .const import DOMAIN

# klucz, pole statusu, komenda, min, max, krok  (zakresy takie same jak w sterowniku)
ITEMS = (
    ("set_boiler", "tempPiecZadana", "SET_PIEC", 40, 90, 1),
    ("set_water", "tempWodaZadana", "SET_WODA", 30, 60, 1),
    ("set_room", "tempPokojuZadana", "SET_TEMP_POKOJU", 15, 30, 0.5),
    ("set_boiler_max_room", "tempPiecMaxRoomMode", "SET_PIEC_MAX_ROOM", 60, 85, 1),
)


async def async_setup_entry(hass, entry, add):
    c = hass.data[DOMAIN][entry.entry_id]
    add(BoilerNumber(c, *i) for i in ITEMS)


class BoilerNumber(BoilerEntity, NumberEntity):
    _attr_device_class = NumberDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator, key, field, cmd, lo, hi, step) -> None:
        super().__init__(coordinator, key)
        self._field, self._cmd = field, cmd
        self._attr_native_min_value, self._attr_native_max_value, self._attr_native_step = lo, hi, step

    @property
    def native_value(self):
        return self.coordinator.data.get(self._field)

    async def async_set_native_value(self, value: float) -> None:
        v = int(value) if float(value).is_integer() else round(value, 1)
        await self.coordinator.send(f"{self._cmd}:{v}")
