"""
Ampster automation template: Control devices based on fetched JSON data.

This file demonstrates how to react to data updates from the coordinator and control Home Assistant devices.

NOTE: The example logic below is commented out by default. Uncomment and adapt it for your own use case.
If you leave it active and the referenced entity_id (e.g., 'switch.inverter') does not exist, Home Assistant will log a warning but the integration will still work.

This automation is triggered whenever new data is fetched (on the hour at the configured minute, or when manually refreshed).
"""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import datetime
import json
import logging

from .const import DOMAIN
# Import the cached timezone objects
from .coordinator import COUNTRY_TZ, DEFAULT_TZ

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    _LOGGER = logging.getLogger(__name__)

    async def handle_data_update():
        # NOTE: For robust automation, it's generally best to use UTC everywhere in your data and comparisons.
        # Localizing to country timezones (as below) is only needed if your data source is not UTC.
        # Consider standardizing all timestamps to UTC in your JSON and logic for simplicity and reliability.
        data = coordinator.data
        if data:
            timestamp = data.get("timestamp")
            country = data.get("country")
            current_period = data.get("current_period")
            _LOGGER.info(f"[Ampster] Data fetched. Timestamp: {timestamp}, Country: {country}, Current Period: {current_period}")

            # Use cached timezone objects to avoid blocking the event loop
            tz = COUNTRY_TZ.get(country, DEFAULT_TZ)

            now = datetime.datetime.now(tz)
            try:
                period_dt = datetime.datetime.fromisoformat(current_period)
                if period_dt.tzinfo is None:
                    period_dt = tz.localize(period_dt)
                if (period_dt.year == now.year and period_dt.month == now.month and
                    period_dt.day == now.day and period_dt.hour == now.hour):
                    _LOGGER.info(f"[Ampster] Data is current (current_period: {period_dt}, now: {now} in {tz})")
                else:
                    _LOGGER.info(f"[Ampster] Data is NOT current (current_period: {period_dt}, now: {now} in {tz})")
            except Exception as e:
                _LOGGER.debug(f"[Ampster] Could not parse or compare current_period: {e}")
        else:
            _LOGGER.info("[Ampster] Data fetched, but no data found!")

    # Log when fetching data, with URL and config
    _LOGGER.info(f"[Ampster] Fetching data from {coordinator.url} (country_prefix={coordinator.country_prefix}, minute={coordinator.minute})")

    def _listener():
        hass.async_create_task(handle_data_update())
    coordinator.async_add_listener(_listener)

    # Call once at startup to fetch/process data immediately
    await handle_data_update()

async def categorise(hass, in_price):
    """Replicates the Jinja categorise macro in Python."""
    try:
        price = float(in_price)
    except (TypeError, ValueError):
        return "Average"

    def get_input_number(name):
        entity = hass.states.get(f"input_number.{name}")
        return float(entity.state) if entity and entity.state not in (None, "", "unknown", "unavailable") else None

    negative = get_input_number("negative")
    very_low = get_input_number("very_low")
    low = get_input_number("low")
    high = get_input_number("high")
    very_high = get_input_number("very_high")

    if negative is not None and price < negative:
        return "Negative"
    elif very_low is not None and price < very_low:
        return "Very Low"
    elif low is not None and price < low:
        return "Low"
    elif very_high is not None and price > very_high:
        return "Very High"
    elif high is not None and price > high:
        return "High"
    else:
        return "Average"

async def calculate_hoarding_periods_remaining(hass):
    """Calculate hoarding periods remaining."""
    # Get current_period as float
    current_hour_attr = hass.states.get("sensor.price_datafeed_12")
    if not current_hour_attr:
        return None
    current_period_str = current_hour_attr.attributes.get("current_hour", "")
    if len(current_period_str) < 13:
        return None
    try:
        current_period = float(current_period_str[11:13])
    except Exception:
        return None

    # Get period_prices as dict
    period_prices_raw = hass.states.get("sensor.hourly_prices_next_12")
    if not period_prices_raw:
        return None
    period_prices_json = period_prices_raw.state.replace("'", '"')
    try:
        period_prices = json.loads(period_prices_json)
    except Exception:
        return None

    ns_hour = -1
    for i in range(12):
        hour = round(i + current_period)
        if hour > 23:
            hour = hour - 24
        price_key = f"{hour:02d}:00"
        cat = await categorise(hass, period_prices.get(price_key))
        if hour > 12 and "High" in cat:
            ns_hour = hour
            break

    if ns_hour < 0:
        max_12_period = hass.states.get("sensor.max_12_period")
        if max_12_period:
            ns_hour = max_12_period.state[10:16]
        else:
            ns_hour = None
    else:
        ns_hour = ns_hour - current_period
        now = datetime.datetime.now()
        if ns_hour > 0:
            ns_hour = ns_hour - (now.minute / 60)
    if ns_hour is not None:
        try:
            ns_hour = round(float(ns_hour), 1)
        except Exception:
            pass
    return ns_hour