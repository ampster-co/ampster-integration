"""
Data uploader for Ampster integration.
Handles posting sensor data to remote server on a schedule.
"""
import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

_LOGGER = logging.getLogger(__name__)

class AmpsterDataUploader:
    """Handles uploading sensor data to remote server."""
    
    def __init__(self, hass: HomeAssistant, upload_url: str, api_key: str, 
                 upload_sensors: str, upload_interval: int):
        self.hass = hass
        self.upload_url = upload_url
        self.api_key = api_key
        self.upload_sensors = [s.strip() for s in upload_sensors.split(",") if s.strip()]
        self.upload_interval = upload_interval
        self._unsub_timer = None
        
    async def async_start(self):
        """Start the periodic upload timer."""
        if self.upload_url and self.api_key and self.upload_sensors:
            interval = timedelta(minutes=self.upload_interval)
            self._unsub_timer = async_track_time_interval(
                self.hass,
                self._async_upload_data,
                interval
            )
            _LOGGER.info(f"[Ampster] Data uploader started - will upload every {self.upload_interval} minutes")
        else:
            _LOGGER.info("[Ampster] Data uploader not started - missing configuration")
    
    async def async_stop(self):
        """Stop the periodic upload timer."""
        if self._unsub_timer:
            self._unsub_timer()
            self._unsub_timer = None
            _LOGGER.info("[Ampster] Data uploader stopped")
    
    async def _async_upload_data(self, now=None):
        """Upload sensor data to remote server."""
        _LOGGER.info(f"[Ampster] _async_upload_data called with now={now}")
        
        if not self.upload_url or not self.api_key or not self.upload_sensors:
            _LOGGER.warning("[Ampster] Upload skipped - missing configuration")
            _LOGGER.debug(f"[Ampster] Config check: url={bool(self.upload_url)}, key={bool(self.api_key)}, sensors={bool(self.upload_sensors)}")
            return
            
        try:
            # Collect sensor data
            _LOGGER.info(f"[Ampster] Starting data collection for sensors: {self.upload_sensors}")
            data = {
                "timestamp": datetime.now().isoformat(),
                "sensors": {}
            }
            
            for sensor_name in self.upload_sensors:
                # Try to find the sensor with different approaches
                entity_id = None
                state = None
                
                if sensor_name.startswith("sensor."):
                    # Full entity ID provided
                    entity_id = sensor_name
                    state = self.hass.states.get(entity_id)
                else:
                    # Try different prefixes in order
                    candidates = [
                        sensor_name,  # Try as-is first (for non-sensor entities)
                        f"sensor.{sensor_name}",  # Try with sensor. prefix
                        f"sensor.ampster_{sensor_name}",  # Try with ampster_ prefix
                    ]
                    
                    for candidate in candidates:
                        state = self.hass.states.get(candidate)
                        if state:
                            entity_id = candidate
                            break
                
                if state:
                    data["sensors"][sensor_name] = {
                        "value": state.state,
                        "attributes": dict(state.attributes)
                    }
                else:
                    _LOGGER.warning(f"[Ampster] Entity '{sensor_name}' not found for upload (tried: {', '.join([sensor_name, f'sensor.{sensor_name}', f'sensor.ampster_{sensor_name}'])})")
            
            if not data["sensors"]:
                _LOGGER.warning("[Ampster] No sensor data found to upload")
                return
            
            _LOGGER.info(f"[Ampster] Collected data for {len(data['sensors'])} sensors: {list(data['sensors'].keys())}")
            
            # Upload data
            headers = {
                "X-API-Key": self.api_key,
                "Content-Type": "application/json"
            }
            
            _LOGGER.info(f"[Ampster] Making HTTP POST to: {self.upload_url}")
            _LOGGER.debug(f"[Ampster] Request headers: {headers}")
            _LOGGER.debug(f"[Ampster] Request payload: {data}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.upload_url, json=data, headers=headers) as response:
                    _LOGGER.info(f"[Ampster] HTTP Response status: {response.status}")
                    _LOGGER.debug(f"[Ampster] Response headers: {dict(response.headers)}")
                    
                    response_text = await response.text()
                    _LOGGER.debug(f"[Ampster] Response body: {response_text}")
                    
                    if response.status == 200:
                        _LOGGER.info(f"[Ampster] Successfully uploaded data for {len(data['sensors'])} sensors")
                    else:
                        _LOGGER.error(f"[Ampster] Upload failed with status {response.status}: {response_text}")
                        
        except Exception as e:
            _LOGGER.error(f"[Ampster] Upload failed with exception: {e}", exc_info=True)
    
    async def async_upload_now(self):
        """Manually trigger an upload now."""
        _LOGGER.info("[Ampster] Manual upload triggered via async_upload_now()")
        try:
            await self._async_upload_data()
            _LOGGER.info("[Ampster] Manual upload completed")
        except Exception as e:
            _LOGGER.error(f"[Ampster] Manual upload failed: {e}", exc_info=True)
