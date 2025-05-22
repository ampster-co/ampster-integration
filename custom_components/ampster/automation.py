"""
Ampster automation template: Control devices based on fetched JSON data.

This file demonstrates how to react to data updates from the coordinator and control Home Assistant devices.

NOTE: The example logic below is commented out by default. Uncomment and adapt it for your own use case.
If you leave it active and the referenced entity_id (e.g., 'switch.inverter') does not exist, Home Assistant will log a warning but the integration will still work.

This automation is triggered whenever new data is fetched (on the hour at the configured minute, or when manually refreshed).
"""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import logging

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    _LOGGER = logging.getLogger(__name__)

    async def handle_data_update():
        data = coordinator.data
        if data:
            timestamp = data.get("timestamp")
            country = data.get("country")
            current_period = data.get("current_period")
            _LOGGER.info(f"[Ampster] Data fetched. Timestamp: {timestamp}, Country: {country}, Current Period: {current_period}")
        else:
            _LOGGER.info("[Ampster] Data fetched, but no data found!")

    # Log when fetching data, with URL and config
    _LOGGER.info(f"[Ampster] Fetching data from {coordinator.url} (country_prefix={coordinator.country_prefix}, minute={coordinator.minute})")

    def _listener():
        hass.async_create_task(handle_data_update())
    coordinator.async_add_listener(_listener)

    # Optionally, call once at startup
    # await handle_data_update()
