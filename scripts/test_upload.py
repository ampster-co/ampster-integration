#!/usr/bin/env python3
"""
Test script for Ampster data upload functionality.

This script simulates the data that would be sent to the upload endpoint.
You can use this to test your remote server endpoint independently.
"""
import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration - update these values to match your setup
UPLOAD_URL = "https://yv3l9alv8g.execute-api.us-east-1.amazonaws.com/prod/data"
API_KEY = "your-api-key-here"

async def test_upload():
    """Test the upload endpoint with sample data."""
    
    # Sample data that would be sent by the integration
    test_data = {
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "country": {
                "value": "NL",
                "attributes": {}
            },
            "current_period_all_in_price": {
                "value": "0.25",
                "attributes": {
                    "unit_of_measurement": "€/kWh"
                }
            },
            "static_42": {
                "value": "42",
                "attributes": {}
            }
        }
    }
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    print(f"Testing upload to: {UPLOAD_URL}")
    print(f"Payload: {json.dumps(test_data, indent=2)}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(UPLOAD_URL, json=test_data, headers=headers) as response:
                print(f"Response status: {response.status}")
                response_text = await response.text()
                print(f"Response body: {response_text}")
                
                if response.status == 200:
                    print("✅ Upload test successful!")
                else:
                    print(f"❌ Upload test failed with status {response.status}")
                    
    except Exception as e:
        print(f"❌ Upload test failed with exception: {e}")

if __name__ == "__main__":
    if API_KEY == "your-api-key-here":
        print("Please update the API_KEY variable in this script before running.")
    else:
        asyncio.run(test_upload())
