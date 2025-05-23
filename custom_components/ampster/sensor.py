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
    entities = []

    # Expose all top-level keys in the fetched JSON as sensors
    if coordinator.data:
        for key, value in coordinator.data.items():
            entities.append(AmpsterSensor(coordinator, key, value))
    
    # Add the custom hoarding periods remaining sensor
    entities.append(AmpsterHoardingPeriodsRemainingSensor(hass, coordinator)) # Pass coordinator
    
    async_add_entities(entities)

class AmpsterSensor(SensorEntity):
    def __init__(self, coordinator, key, value):
        self.coordinator = coordinator
        self._key = key
        self._attr_name = f"Ampster {key}"
        self._attr_unique_id = f"ampster_{key}"
        # Only set the state to a short value (max 255 chars)
        if isinstance(value, (str, int, float)) and len(str(value)) <= 255:
            self._attr_native_value = value
        else:
            # For long or complex values, set a summary or count
            if isinstance(value, dict):
                self._attr_native_value = f"dict ({len(value)})"
            elif isinstance(value, list):
                self._attr_native_value = f"list ({len(value)})"
            else:
                self._attr_native_value = str(value)[:255]
        self._attr_extra_state_attributes = {"full_value": value} if isinstance(value, (dict, list)) else {}

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def native_value(self):
        value = self.coordinator.data.get(self._key)
        if isinstance(value, (str, int, float)) and len(str(value)) <= 255:
            return value
        elif isinstance(value, dict):
            return f"dict ({len(value)})"
        elif isinstance(value, list):
            return f"list ({len(value)})"
        else:
            return str(value)[:255]

    @property
    def extra_state_attributes(self):
        value = self.coordinator.data.get(self._key)
        if isinstance(value, (dict, list)):
            return {"full_value": value}
        return {}

class AmpsterHoardingPeriodsRemainingSensor(SensorEntity):
    _attr_name = "Ampster Hoarding Periods Remaining"
    _attr_unique_id = "ampster_hoarding_periods_remaining"
    _attr_should_poll = False

    def __init__(self, hass, coordinator):
        self.hass = hass
        self.coordinator = coordinator
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.country_prefix)},
            "name": "Ampster",
            "manufacturer": "Ampster",
            "entry_type": "service",
        }

    async def async_added_to_hass(self) -> None:
        """Connect to coordinator for updates."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    async def async_update(self):
        from .automation import calculate_hoarding_periods_remaining
        # Make sure to pass hass to the calculation function if it needs it
        # and potentially other data from the coordinator if required
        self._attr_native_value = await calculate_hoarding_periods_remaining(self.hass)

# To disable exposing sensors, remove or comment out this file and its setup in __init__.py