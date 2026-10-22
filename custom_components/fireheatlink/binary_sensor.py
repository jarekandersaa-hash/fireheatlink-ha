from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity

from . import BoilerEntity
from .const import DOMAIN
from .sensor import is_alarm

# klucz, klasa, funkcja, (opcjonalnie) kiedy encja jest dostepna
ITEMS = (
    ("alarm", BinarySensorDeviceClass.PROBLEM, is_alarm),
    ("pump_heating", BinarySensorDeviceClass.RUNNING, lambda d: bool(d.get("pompGrzejniki"))),
    ("pump_dhw", BinarySensorDeviceClass.RUNNING, lambda d: bool(d.get("pompCW"))),
    ("auger", BinarySensorDeviceClass.RUNNING, lambda d: bool(d.get("slimak"))),
    # zawor trojdrozny (jedna pompa dla grzejnikow i zasobnika): wlaczony = woda idzie na zasobnik
    ("valve_tank", BinarySensorDeviceClass.RUNNING, lambda d: bool(d.get("pompCW")), lambda d: bool(d.get("dhwValve"))),
    # ostrzezenia z czujnika powrotu (nie zatrzymuja pieca)
    ("warn_no_flow", BinarySensorDeviceClass.PROBLEM, lambda d: bool((d.get("warn") or 0) & 16), lambda d: bool(d.get("retSet"))),
    ("warn_radiators", BinarySensorDeviceClass.PROBLEM, lambda d: bool((d.get("warn") or 0) & 32), lambda d: bool(d.get("retSet"))),
)


async def async_setup_entry(hass, entry, add):
    c = hass.data[DOMAIN][entry.entry_id]
    add(BoilerBinary(c, *i) for i in ITEMS)


class BoilerBinary(BoilerEntity, BinarySensorEntity):
    def __init__(self, coordinator, key, dev_class, fn, avail=None) -> None:
        super().__init__(coordinator, key)
        self._attr_device_class = dev_class
        self._fn = fn
        self._avail = avail

    @property
    def available(self) -> bool:
        return super().available and (self._avail is None or self._avail(self.coordinator.data))

    @property
    def is_on(self) -> bool:
        return self._fn(self.coordinator.data)
