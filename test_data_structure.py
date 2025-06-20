#!/usr/bin/env python3
"""
Test script to simulate the Home Assistant domain data structure
and verify the uploader storage and retrieval logic.
"""

# Simulate the hass.data structure
DOMAIN = "ampster"
entry_id = "test_entry_123"

# Simulate hass.data
hass_data = {
    DOMAIN: {}
}

print("=== Testing Ampster uploader storage and retrieval ===")

# Simulate coordinator storage
print(f"1. Storing coordinator in hass.data[{DOMAIN}][{entry_id}]")
hass_data[DOMAIN][entry_id] = "coordinator_object"

# Simulate uploader storage
uploader_key = f"{entry_id}_uploader"
print(f"2. Storing uploader in hass.data[{DOMAIN}][{uploader_key}]")
hass_data[DOMAIN][uploader_key] = "uploader_object"

print(f"3. Current hass.data structure:")
print(f"   hass.data[{DOMAIN}] = {hass_data[DOMAIN]}")

# Simulate button setup
print(f"\n4. Button setup simulation:")
print(f"   Looking for coordinator: hass.data[{DOMAIN}][{entry_id}]")
coordinator = hass_data[DOMAIN][entry_id]
print(f"   Found coordinator: {coordinator}")

print(f"   Looking for uploader: hass.data[{DOMAIN}].get('{uploader_key}')")
uploader = hass_data[DOMAIN].get(uploader_key)
print(f"   Found uploader: {uploader}")

if uploader:
    print("   ✅ Upload button would be created")
else:
    print("   ❌ Upload button would NOT be created")
    print(f"   Available keys: {list(hass_data[DOMAIN].keys())}")
