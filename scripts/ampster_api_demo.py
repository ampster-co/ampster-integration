#!/usr/bin/env python3
"""
Ampster Home Assistant API Demo Script

- Fetches all sensors created by the Ampster integration
- Presses the Ampster update button to refresh data

Usage:
  Set the following environment variables or edit the script directly:
    HA_URL: Home Assistant base URL (e.g. http://homeassistant.local:8123)
    HA_TOKEN: Your long-lived access token

You can generate a long-lived access token in your Home Assistant user profile (bottom of the page):
  http://homeassistant.local:8123/profile/security
"""
import os
import requests
import sys

HA_URL = os.getenv("HA_URL", "http://homeassistant.local:8123")
HA_TOKEN = os.getenv("HA_TOKEN", "YOUR_LONG_LIVED_ACCESS_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}

# Helper to print and exit on error
def die(msg):
    print(f"Error: {msg}")
    sys.exit(1)

if not HA_TOKEN or HA_TOKEN == "YOUR_LONG_LIVED_ACCESS_TOKEN":
    die("Please set your Home Assistant long-lived access token in HA_TOKEN or as an environment variable.")

# 1. Get all states and filter for Ampster sensors
resp = requests.get(f"{HA_URL}/api/states", headers=HEADERS)
if resp.status_code != 200:
    die(f"Failed to fetch states: {resp.text}")

states = resp.json()
ampster_sensors = [s for s in states if s["entity_id"].startswith("sensor.ampster_")]

print("Ampster Sensors:")
for s in ampster_sensors:
    print(f"  {s['entity_id']}: {s['state']}")

# 2. Press the Ampster update button
button_entity_id = "button.ampster_update_now"
print(f"\nPressing button: {button_entity_id}")
service_url = f"{HA_URL}/api/services/button/press"
resp = requests.post(service_url, headers=HEADERS, json={"entity_id": button_entity_id})
if resp.status_code == 200:
    print("Button press successful!")
else:
    print(f"Button press failed: {resp.text}")
