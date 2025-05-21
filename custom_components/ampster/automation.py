"""
Ampster automation template: Control devices based on fetched JSON data.

This file demonstrates how to react to data updates from the coordinator and control Home Assistant devices.

NOTE: The example logic below is commented out by default. Uncomment and adapt it for your own use case.
If you leave it active and the referenced entity_id (e.g., 'switch.inverter') does not exist, Home Assistant will log a warning but the integration will still work.

This automation is triggered whenever new data is fetched (on the hour at the configured minute, or when manually refreshed).
"""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import HomeAssistantType

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async def handle_data_update():
        data = coordinator.data
        # Example: If the current all-in price is below 0.20 EUR/kWh, turn on the inverter
        # Otherwise, turn it off
        # Uncomment and adapt the logic below for your setup:
        # if data:
        #     current_price = data.get("current_period_all_in_price")
        #     if current_price is not None:
        #         if current_price < 0.20:
        #             await hass.services.async_call(
        #                 'switch', 'turn_on',
        #                 { 'entity_id': 'switch.inverter' },
        #                 blocking=True
        #             )
        #         else:
        #             await hass.services.async_call(
        #                 'switch', 'turn_off',
        #                 { 'entity_id': 'switch.inverter' },
        #                 blocking=True
        #             )

    # Listen for coordinator data updates
    coordinator.async_add_listener(handle_data_update)

    # Optionally, call once at startup
    # await handle_data_update()

# To use: Uncomment and adapt the logic above, then import and call async_setup_entry from __init__.py
