"""Config flow for Ampster integration."""
from homeassistant import config_entries
from homeassistant.core import callback
from .const import (
    DOMAIN, DEFAULT_COUNTRY, DEFAULT_MINUTE, DEFAULT_BASE_URL, SUPPORTED_COUNTRIES,
    DEFAULT_UPLOAD_URL, DEFAULT_UPLOAD_INTERVAL, DEFAULT_UPLOAD_SENSORS, DEFAULT_API_KEY
)

class AmpsterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ampster."""

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Validate and create entry
            return self.async_create_entry(title="Ampster Home Integration", data=user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=self._get_schema(),
            errors=errors,
            description_placeholders={
                "title": "Ampster Home Integration"
            },
        )

    async def async_step_options(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Ampster Home Integration Options", data=user_input)
        # Use current config entry values as defaults
        entry = self._current_entry
        current_country = entry.data.get("country_prefix", DEFAULT_COUNTRY)
        current_minute = entry.data.get("minute", DEFAULT_MINUTE)
        current_base_url = entry.data.get("base_url", DEFAULT_BASE_URL)
        current_upload_url = entry.options.get("upload_url", entry.data.get("upload_url", DEFAULT_UPLOAD_URL))
        current_api_key = entry.options.get("api_key", entry.data.get("api_key", DEFAULT_API_KEY))
        current_upload_sensors = entry.options.get("upload_sensors", entry.data.get("upload_sensors", DEFAULT_UPLOAD_SENSORS))
        current_upload_interval = entry.options.get("upload_interval", entry.data.get("upload_interval", DEFAULT_UPLOAD_INTERVAL))
        return self.async_show_form(
            step_id="options",
            data_schema=self._get_schema(
                minute=current_minute, 
                base_url=current_base_url,
                upload_url=current_upload_url,
                api_key=current_api_key,
                upload_sensors=current_upload_sensors,
                upload_interval=current_upload_interval
            ),
            errors=errors,
            description_placeholders={
                "title": "Ampster Home Integration Options"
            },
        )

    @callback
    def _get_schema(self, minute=DEFAULT_MINUTE, base_url=DEFAULT_BASE_URL, upload_url=DEFAULT_UPLOAD_URL, 
                   api_key=DEFAULT_API_KEY, upload_sensors=DEFAULT_UPLOAD_SENSORS, upload_interval=DEFAULT_UPLOAD_INTERVAL):
        from homeassistant.helpers import config_validation as cv
        import voluptuous as vol
        # Guess country prefix from locale
        lang_map = {
            "nl": "NL",
            "fr": "FR",
            "be": "BE",
            "de": "AT",  # Example: map 'de' to 'AT', adjust as needed
            "at": "AT",
        }
        hass_lang = (self.hass.config.language or "en").lower()
        guessed_prefix = lang_map.get(hass_lang, DEFAULT_COUNTRY)
        country_options = SUPPORTED_COUNTRIES
        return vol.Schema({
            vol.Required("country_prefix", default=guessed_prefix): vol.In(country_options),
            vol.Required("minute", default=minute): vol.All(vol.Coerce(int), vol.Range(min=0, max=59)),
            vol.Required("base_url", default=base_url): str,
            vol.Optional("upload_url", default=upload_url): str,
            vol.Optional("api_key", default=api_key): str,
            vol.Optional("upload_sensors", default=upload_sensors): str,
            vol.Optional("upload_interval", default=upload_interval): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
        })

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return AmpsterOptionsFlowHandler(config_entry)

class AmpsterOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, entry):
        self._entry = entry

    @property
    def config_entry(self):
        return self._entry

    async def async_step_init(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Ampster Home Integration Options", data=user_input)
        current_country = self.config_entry.options.get("country_prefix", self.config_entry.data.get("country_prefix", DEFAULT_COUNTRY))
        current_minute = self.config_entry.options.get("minute", self.config_entry.data.get("minute", DEFAULT_MINUTE))
        current_base_url = self.config_entry.options.get("base_url", self.config_entry.data.get("base_url", DEFAULT_BASE_URL))
        current_upload_url = self.config_entry.options.get("upload_url", self.config_entry.data.get("upload_url", DEFAULT_UPLOAD_URL))
        current_api_key = self.config_entry.options.get("api_key", self.config_entry.data.get("api_key", DEFAULT_API_KEY))
        current_upload_sensors = self.config_entry.options.get("upload_sensors", self.config_entry.data.get("upload_sensors", DEFAULT_UPLOAD_SENSORS))
        current_upload_interval = self.config_entry.options.get("upload_interval", self.config_entry.data.get("upload_interval", DEFAULT_UPLOAD_INTERVAL))
        from homeassistant.helpers import config_validation as cv
        import voluptuous as vol
        country_options = SUPPORTED_COUNTRIES
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("country_prefix", default=current_country): vol.In(country_options),
                vol.Required("minute", default=current_minute): vol.All(vol.Coerce(int), vol.Range(min=0, max=59)),
                vol.Required("base_url", default=current_base_url): str,
                vol.Optional("upload_url", default=current_upload_url): str,
                vol.Optional("api_key", default=current_api_key): str,
                vol.Optional("upload_sensors", default=current_upload_sensors): str,
                vol.Optional("upload_interval", default=current_upload_interval): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
            }),
            errors=errors,
            description_placeholders={
                "title": "Ampster Home Integration Options"
            },
        )
