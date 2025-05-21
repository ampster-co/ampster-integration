"""
Ampster sensor platform to expose fetched JSON data as sensors.
"""
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    # Expose all top-level keys in the fetched JSON as sensors
    entities = []
    if coordinator.data:
        for key, value in coordinator.data.items():
            entities.append(AmpsterSensor(coordinator, key, value))
    async_add_entities(entities)

class AmpsterSensor(SensorEntity):
    def __init__(self, coordinator, key, value):
        self.coordinator = coordinator
        self._key = key
        self._attr_name = f"Ampster {key}"
        self._attr_unique_id = f"ampster_{key}"
        self._attr_native_value = value

    @property
    def native_value(self):
        # Update value from coordinator data
        return self.coordinator.data.get(self._key)

    async def async_update(self):
        await self.coordinator.async_request_refresh()

# To disable exposing sensors, remove or comment out this file and its setup in __init__.py
