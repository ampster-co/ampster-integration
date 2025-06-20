"""
Ampster Update Now Button platform.
"""
import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    uploader = hass.data[DOMAIN].get(f"{entry.entry_id}_uploader")
    
    buttons = [AmpsterUpdateNowButton(coordinator)]
    
    # Add upload button if uploader is configured
    if uploader:
        _LOGGER.info(f"[Ampster] Adding upload button - uploader found: {uploader}")
        buttons.append(AmpsterUploadNowButton(uploader))
    else:
        _LOGGER.info(f"[Ampster] No upload button added - uploader not found in hass.data[{DOMAIN}]")
        _LOGGER.debug(f"[Ampster] Available domain data keys: {list(hass.data.get(DOMAIN, {}).keys())}")
        # For debugging, let's create a dummy upload button anyway
        _LOGGER.info("[Ampster] Creating dummy upload button for debugging")
        buttons.append(AmpsterUploadNowButton(None))
    
    async_add_entities(buttons)

class AmpsterUpdateNowButton(ButtonEntity):
    _attr_name = "Ampster: Update Now"
    _attr_unique_id = "ampster_update_now"

    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.country_prefix)},
            "name": "Ampster",
            "manufacturer": "Ampster",
            "entry_type": "service",
        }

    async def async_press(self) -> None:
        await self.coordinator.async_request_refresh()

class AmpsterUploadNowButton(ButtonEntity):
    _attr_name = "Ampster: Upload Now"
    _attr_unique_id = "ampster_upload_now"

    def __init__(self, uploader):
        self.uploader = uploader
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "ampster_uploader")},
            "name": "Ampster",
            "manufacturer": "Ampster",
            "entry_type": "service",
        }

    async def async_press(self) -> None:
        _LOGGER.info("[Ampster] Upload Now button pressed!")
        if self.uploader:
            _LOGGER.info(f"[Ampster] Calling uploader.async_upload_now() on {self.uploader}")
            await self.uploader.async_upload_now()
        else:
            _LOGGER.error("[Ampster] Upload button pressed but no uploader available!")
