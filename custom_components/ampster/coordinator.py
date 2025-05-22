"""
Ampster DataUpdateCoordinator for periodic JSON fetching.
"""
import logging
from datetime import timedelta
import aiohttp
import pytz
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.event import async_track_time_change
from .const import DOMAIN, DEFAULT_COUNTRY, DEFAULT_MINUTE, BASE_URL, SUPPORTED_COUNTRIES

_LOGGER = logging.getLogger(__name__)

# Cache timezone objects at module level to avoid blocking calls in the event loop
COUNTRY_TZ = {
    "NL": pytz.timezone("Europe/Amsterdam"),
    "BE": pytz.timezone("Europe/Brussels"),
    "FR": pytz.timezone("Europe/Paris"),
    "AT": pytz.timezone("Europe/Vienna"),
}
DEFAULT_TZ = pytz.UTC

class AmpsterDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, url: str = None, country_prefix: str = None, minute: int = DEFAULT_MINUTE):
        self.hass = hass
        self.country_prefix = country_prefix
        self.minute = minute
        # Determine country prefix from locale if not provided
        if not self.country_prefix:
            lang = (hass.config.language or "en").lower()
            lang_map = {
                "nl": "NL",
                "fr": "FR",
                "be": "BE",
                "de": "AT",  # Example: map 'de' to 'AT', adjust as needed
                "at": "AT",
            }
            self.country_prefix = lang_map.get(lang, DEFAULT_COUNTRY)
        self.url = url or f"{BASE_URL}{self.country_prefix}.json"
        super().__init__(
            hass,
            _LOGGER,
            name="Ampster Data Coordinator",
            update_interval=None,  # We'll schedule updates manually
        )
        self._unsub_timer = async_track_time_change(
            hass,
            self._scheduled_refresh,
            minute=self.minute,
            second=0,
        )

    async def _async_update_data(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as err:
            _LOGGER.error(f"[Ampster] Data fetch failed: {err}")
            raise UpdateFailed(f"Error fetching data: {err}")

    async def _scheduled_refresh(self, now):
        _LOGGER.info(f"[Ampster] Scheduled refresh fired at {now.isoformat()} (should be every hour at minute={self.minute})")
        await self.async_request_refresh()

    async def async_shutdown(self):
        if self._unsub_timer:
            self._unsub_timer()
            self._unsub_timer = None
