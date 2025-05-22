"""Ampster Home Assistant integration setup."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .automation import async_setup_entry as async_setup_automation_entry
from .coordinator import AmpsterDataUpdateCoordinator

DOMAIN = "ampster"

PLATFORMS = ["button", "sensor"]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Ampster integration via configuration.yaml (not used)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ampster from a config entry."""
    # Prefer options over data for config values
    country_prefix = entry.options.get("country_prefix") if entry.options.get("country_prefix") is not None else entry.data.get("country_prefix")
    minute = entry.options.get("minute") if entry.options.get("minute") is not None else entry.data.get("minute", 2)
    coordinator = AmpsterDataUpdateCoordinator(hass, country_prefix=country_prefix, minute=minute)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    # Use standard platform forwarding for button and sensor only
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    # Set up the automation logic to control devices based on data
    await async_setup_automation_entry(hass, entry)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an Ampster config entry."""
    # Unload platforms first
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    # Remove coordinator and shut it down
    coordinator = hass.data[DOMAIN].pop(entry.entry_id, None)
    if coordinator:
        await coordinator.async_shutdown()
    return unload_ok
