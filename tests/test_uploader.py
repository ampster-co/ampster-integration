import pytest
import aiohttp
from unittest.mock import AsyncMock, MagicMock, patch
from custom_components.ampster.uploader import AmpsterDataUploader

class DummyHass:
    def __init__(self):
        self.states = MagicMock()

@pytest.mark.asyncio
async def test_ampster_data_uploader_initialization():
    """Test uploader initialization."""
    hass = DummyHass()
    uploader = AmpsterDataUploader(
        hass=hass,
        upload_url="https://example.com/api",
        api_key="test-key",
        upload_sensors="sensor1,sensor2",
        upload_interval=15
    )
    
    assert uploader.upload_url == "https://example.com/api"
    assert uploader.api_key == "test-key"
    assert uploader.upload_sensors == ["sensor1", "sensor2"]
    assert uploader.upload_interval == 15

@pytest.mark.asyncio
async def test_ampster_data_uploader_manual_upload():
    """Test manual upload functionality."""
    hass = DummyHass()
    
    # Mock sensor states
    mock_state = MagicMock()
    mock_state.state = "42"
    mock_state.attributes = {"unit": "test"}
    hass.states.get.return_value = mock_state
    
    uploader = AmpsterDataUploader(
        hass=hass,
        upload_url="https://example.com/api",
        api_key="test-key",
        upload_sensors="test_sensor",
        upload_interval=15
    )
    
    # Mock aiohttp session and response
    with patch('aiohttp.ClientSession') as mock_session:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        
        mock_session.return_value.__aenter__.return_value.post.return_value = mock_response
        
        await uploader.async_upload_now()
        
        # Verify the session was used
        mock_session.assert_called_once()
