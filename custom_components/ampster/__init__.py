"""Ampster Home Assistant integration setup."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .automation import async_setup_entry as async_setup_automation_entry
from .coordinator import AmpsterDataUpdateCoordinator
from .uploader import AmpsterDataUploader

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
    base_url = entry.options.get("base_url") if entry.options.get("base_url") is not None else entry.data.get("base_url", None)
    
    # Get upload configuration
    upload_url = entry.options.get("upload_url") if entry.options.get("upload_url") is not None else entry.data.get("upload_url", "")
    api_key = entry.options.get("api_key") if entry.options.get("api_key") is not None else entry.data.get("api_key", "")
    upload_sensors = entry.options.get("upload_sensors") if entry.options.get("upload_sensors") is not None else entry.data.get("upload_sensors", "")
    upload_interval = entry.options.get("upload_interval") if entry.options.get("upload_interval") is not None else entry.data.get("upload_interval", 15)
    
    from .const import DEFAULT_BASE_URL
    if not base_url:
        base_url = DEFAULT_BASE_URL
        
    coordinator = AmpsterDataUpdateCoordinator(hass, country_prefix=country_prefix, minute=minute, url=None, base_url=base_url)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    
    # Set up data uploader if configured
    uploader = None
    if upload_url and api_key and upload_sensors:
        uploader = AmpsterDataUploader(hass, upload_url, api_key, upload_sensors, upload_interval)
        await uploader.async_start()
        hass.data[DOMAIN][f"{entry.entry_id}_uploader"] = uploader
    
    # Use standard platform forwarding for button and sensor only
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    # Set up the automation logic to control devices based on data
    await async_setup_automation_entry(hass, entry)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an Ampster config entry."""
    # Stop uploader if it exists
    uploader = hass.data[DOMAIN].pop(f"{entry.entry_id}_uploader", None)
    if uploader:
        await uploader.async_stop()
    
    # Unload platforms first
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    # Remove coordinator and shut it down
    coordinator = hass.data[DOMAIN].pop(entry.entry_id, None)
    if coordinator:
        await coordinator.async_shutdown()
    return unload_ok
