"""
Ampster Update Now Button platform.
"""
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    uploader = hass.data[DOMAIN].get(f"{entry.entry_id}_uploader")
    
    buttons = [AmpsterUpdateNowButton(coordinator)]
    
    # Add upload button if uploader is configured
    if uploader:
        buttons.append(AmpsterUploadNowButton(uploader))
    
    async_add_entities(buttons)

class AmpsterUpdateNowButton(ButtonEntity):
    _attr_name = "Ampster: Update Now"
    _attr_unique_id = "ampster_update_now"

    def __init__(self, coordinator):
        self.coordinator = coordinator

    async def async_press(self) -> None:
        await self.coordinator.async_request_refresh()

class AmpsterUploadNowButton(ButtonEntity):
    _attr_name = "Ampster: Upload Now"
    _attr_unique_id = "ampster_upload_now"

    def __init__(self, uploader):
        self.uploader = uploader

    async def async_press(self) -> None:
        await self.uploader.async_upload_now()
