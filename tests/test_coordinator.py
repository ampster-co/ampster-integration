import pytest
from homeassistant.core import HomeAssistant
from custom_components.ampster.coordinator import AmpsterDataUpdateCoordinator

import asyncio

class MockResponse:
    def __init__(self, json_data):
        self._json = json_data
    async def json(self):
        return self._json
    def raise_for_status(self):
        pass

class MockSession:
    def __init__(self, json_data):
        self._json = json_data
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass
    async def get(self, url):
        return MockResponse(self._json)

@pytest.mark.asyncio
async def test_coordinator_fetch(monkeypatch):
    """Test that the coordinator fetches and parses data correctly."""
    test_json = {"current_period_all_in_price": 0.123, "country": "NL"}
    hass = HomeAssistant()
    # Patch aiohttp.ClientSession to use our mock
    monkeypatch.setattr("aiohttp.ClientSession", lambda *a, **kw: MockSession(test_json))
    coordinator = AmpsterDataUpdateCoordinator(hass, country_prefix="NL", minute=2)
    data = await coordinator._async_update_data()
    assert data["current_period_all_in_price"] == 0.123
    assert data["country"] == "NL"
