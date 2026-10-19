from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity

from . import BoilerEntity
from .const import DOMAIN
from .sensor import is_alarm

# klucz, klasa, funkcja
ITEMS = (
    ("alarm", BinarySensorDeviceClass.PROBLEM, is_alarm),
    ("pump_heating", BinarySensorDeviceClass.RUNNING, lambda d: bool(d.get("pompGrzejniki"))),
    ("pump_dhw", BinarySensorDeviceClass.RUNNING, lambda d: bool(d.get("pompCW"))),
    ("auger", BinarySensorDeviceClass.RUNNING, lambda d: bool(d.get("slimak"))),
)


async def async_setup_entry(hass, entry, add):
    c = hass.data[DOMAIN][entry.entry_id]
    add(BoilerBinary(c, *i) for i in ITEMS)


class BoilerBinary(BoilerEntity, BinarySensorEntity):
    def __init__(self, coordinator, key, dev_class, fn) -> None:
        super().__init__(coordinator, key)
        self._attr_device_class = dev_class
        self._fn = fn

    @property
    def is_on(self) -> bool:
        return self._fn(self.coordinator.data)
