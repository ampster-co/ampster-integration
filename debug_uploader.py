#!/usr/bin/env python3
"""
Debug script to test the Ampster uploader outside of Home Assistant.
This can help identify if the issue is with the uploader itself or the integration.
"""
import asyncio
import logging
import sys
import os

# Add the custom_components path to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components'))

from ampster.uploader import AmpsterDataUploader

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class MockHomeAssistant:
    """Mock Home Assistant object for testing."""
    
    def __init__(self):
        self.states = MockStates()

class MockStates:
    """Mock states registry."""
    
    def __init__(self):
        self._states = {
            "sensor.ampster_static_42": MockState("42", {"unit_of_measurement": "€"}),
            "sensor.test_sensor": MockState("123.45", {"unit_of_measurement": "kWh"}),
        }
    
    def get(self, entity_id):
        return self._states.get(entity_id)

class MockState:
    """Mock state object."""
    
    def __init__(self, state, attributes):
        self.state = state
        self.attributes = attributes

async def test_uploader():
    """Test the uploader functionality."""
    print("Testing Ampster uploader...")
    
    # Create mock Home Assistant
    hass = MockHomeAssistant()
    
    # Configure uploader
    upload_url = "https://yv3l9alv8g.execute-api.us-east-1.amazonaws.com/prod/data"
    api_key = ""
    upload_sensors = "static_42,test_sensor"
    upload_interval = 15
    
    # Create uploader
    uploader = AmpsterDataUploader(hass, upload_url, api_key, upload_sensors, upload_interval)
    
    print(f"Created uploader: {uploader}")
    print(f"Upload URL: {uploader.upload_url}")
    print(f"API Key: {uploader.api_key}")
    print(f"Sensors: {uploader.upload_sensors}")
    print(f"Interval: {uploader.upload_interval}")
    
    # Test manual upload
    print("\nTesting manual upload...")
    await uploader.async_upload_now()
    
    print("Test completed.")

if __name__ == "__main__":
    asyncio.run(test_uploader())
