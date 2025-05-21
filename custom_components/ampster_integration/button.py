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
    async_add_entities([
        AmpsterUpdateNowButton(coordinator)
    ])

class AmpsterUpdateNowButton(ButtonEntity):
    _attr_name = "Ampster: Update Now"
    _attr_unique_id = "ampster_update_now"

    def __init__(self, coordinator):
        self.coordinator = coordinator

    async def async_press(self) -> None:
        await self.coordinator.async_request_refresh()
