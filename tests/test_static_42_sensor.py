import pytest
import aiohttp
from custom_components.ampster.sensor import AmpsterStatic42Sensor

class DummyCoordinator:
    country_prefix = "NL"
    last_update_success = True
    def __init__(self, data):
        self.data = data

@pytest.mark.asyncio
async def test_ampster_static_42_sensor_returns_42():
    # Fetch live data
    url = "https://ampster.s3.us-east-1.amazonaws.com/electricity_prices/NL.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            assert resp.status == 200
            data = await resp.json()
    coordinator = DummyCoordinator(data)
    sensor = AmpsterStatic42Sensor(None, coordinator)
    await sensor.async_update()
    assert sensor.native_value == 42
    assert sensor.available is True
    assert sensor._attr_name == "Ampster Static 42"
    assert sensor._attr_unique_id == "ampster_static_42"
