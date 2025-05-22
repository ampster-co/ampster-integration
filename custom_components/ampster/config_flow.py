"""Config flow for Ampster integration."""
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, DEFAULT_COUNTRY, DEFAULT_MINUTE, SUPPORTED_COUNTRIES

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
        return self.async_show_form(
            step_id="options",
            data_schema=self._get_schema(minute=current_minute),
            errors=errors,
            description_placeholders={
                "title": "Ampster Home Integration Options"
            },
        )

    @callback
    def _get_schema(self, minute=DEFAULT_MINUTE):
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
        from homeassistant.helpers import config_validation as cv
        import voluptuous as vol
        country_options = SUPPORTED_COUNTRIES
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("country_prefix", default=current_country): vol.In(country_options),
                vol.Required("minute", default=current_minute): vol.All(vol.Coerce(int), vol.Range(min=0, max=59)),
            }),
            errors=errors,
            description_placeholders={
                "title": "Ampster Home Integration Options"
            },
        )
