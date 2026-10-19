from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import PERCENTAGE, SIGNAL_STRENGTH_DECIBELS_MILLIWATT, UnitOfMass, UnitOfTemperature
from homeassistant.helpers.entity import EntityCategory

from . import BoilerEntity
from .const import DOMAIN


def is_alarm(d: dict) -> bool:
    return bool(d.get("alarmCritical") or d.get("emergencyStop") or d.get("safety"))


def _state(d: dict) -> str:
    if is_alarm(d):
        return "alarm"
    if not d.get("running"):
        return "stopped"
    return "manual" if d.get("manualMode") else "auto"


def _fuel_kg(d: dict) -> float | None:
    f = d.get("fuel") or {}
    if not f.get("en") or not f.get("gps"):
        return None
    return round(f["gps"] * f.get("sec", 0) / 1000.0, 1)


@dataclass(frozen=True, kw_only=True)
class Desc(SensorEntityDescription):
    value: Callable[[dict], Any]
    available: Callable[[dict], bool] = lambda d: True


TEMP = dict(device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT)

SENSORS: tuple[Desc, ...] = (
    Desc(key="state", translation_key="state", device_class=SensorDeviceClass.ENUM,
         options=["stopped", "auto", "manual", "alarm"], value=_state),
    Desc(key="temp_boiler", translation_key="temp_boiler", value=lambda d: d.get("tempPiec"), **TEMP),
    Desc(key="temp_water", translation_key="temp_water", value=lambda d: d.get("tempWoda"), **TEMP),
    Desc(key="temp_auger", translation_key="temp_auger", value=lambda d: d.get("tempSlimak"), **TEMP),
    Desc(key="temp_room", translation_key="temp_room", value=lambda d: d.get("tempPokoju"),
         available=lambda d: bool(d.get("roomSensorConnected")), **TEMP),
    Desc(key="temp_flue", translation_key="temp_flue", value=lambda d: d.get("flueTemp"),
         available=lambda d: bool(d.get("flueEnabled")), **TEMP),
    Desc(key="blower", translation_key="blower", native_unit_of_measurement=PERCENTAGE,
         state_class=SensorStateClass.MEASUREMENT, value=lambda d: d.get("dmuchawa")),
    Desc(key="fuel_total", translation_key="fuel_total", device_class=SensorDeviceClass.WEIGHT,
         native_unit_of_measurement=UnitOfMass.KILOGRAMS, state_class=SensorStateClass.TOTAL_INCREASING,
         value=_fuel_kg, available=lambda d: _fuel_kg(d) is not None),
    Desc(key="wifi_rssi", translation_key="wifi_rssi", device_class=SensorDeviceClass.SIGNAL_STRENGTH,
         native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT, entity_category=EntityCategory.DIAGNOSTIC,
         entity_registry_enabled_default=False, value=lambda d: d.get("wifiRssi")),
)


async def async_setup_entry(hass, entry, add):
    c = hass.data[DOMAIN][entry.entry_id]
    add(BoilerSensor(c, d) for d in SENSORS)


class BoilerSensor(BoilerEntity, SensorEntity):
    entity_description: Desc

    def __init__(self, coordinator, desc: Desc) -> None:
        super().__init__(coordinator, desc.key)
        self.entity_description = desc

    @property
    def available(self) -> bool:
        return super().available and self.entity_description.available(self.coordinator.data)

    @property
    def native_value(self):
        return self.entity_description.value(self.coordinator.data)
