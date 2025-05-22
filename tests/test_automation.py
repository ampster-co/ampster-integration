"""
Test for automation.py logic in the Ampster integration.

This test provides a basic structure for testing the automation logic. 
You should expand it as you add more logic to automation.py.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import aiohttp
import asyncio
from custom_components.ampster import automation
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

class DummyCoordinator:
    def __init__(self, data, url="https://ampster.s3.us-east-1.amazonaws.com/electricity_prices/NL.json", country_prefix="NL", minute=2):
        self.data = data
        self.url = url
        self.country_prefix = country_prefix
        self.minute = minute
        self._listeners = []
    def async_add_listener(self, listener):
        self._listeners.append(listener)
    async def trigger_update(self):
        for listener in self._listeners:
            listener()

@pytest.mark.asyncio
async def test_handle_data_update_triggers_log(monkeypatch, caplog):
    """
    Fetch live data and test that handle_data_update logs expected info when triggered.
    """
    # Fetch live data
    url = "https://ampster.s3.us-east-1.amazonaws.com/electricity_prices/NL.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            assert resp.status == 200
            data = await resp.json()

    # Dummy HomeAssistant and ConfigEntry
    class DummyHass:
        def __init__(self):
            self.data = {automation.DOMAIN: {"dummy_entry": None}}
        def async_create_task(self, coro):
            # Run the coroutine immediately for test
            asyncio.get_event_loop().create_task(coro)
    class DummyEntry:
        entry_id = "dummy_entry"

    hass = DummyHass()
    entry = DummyEntry()
    coordinator = DummyCoordinator(data)
    hass.data[automation.DOMAIN][entry.entry_id] = coordinator

    # Patch logging to capture logs
    caplog.set_level("INFO")

    # Run async_setup_entry, which will register the listener
    await automation.async_setup_entry(hass, entry)

    # Trigger the update (simulate data fetch)
    await coordinator.trigger_update()
    await asyncio.sleep(0.1)  # Let log flush

    # Check that log contains expected info
    assert any("Data fetched" in record.message for record in caplog.records)
