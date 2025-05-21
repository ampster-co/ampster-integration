# Ampster Home Assistant Custom Integration

## Overview
This custom integration fetches electricity price data for a selected country from a remote server (Ampster S3 bucket) and exposes it in Home Assistant. It also provides automation logic to control devices (e.g., an inverter) based on the fetched data, and includes a manual update button.

## File Structure and Responsibilities

- `__init__.py`: Main entry point. Sets up the integration, initializes the data coordinator, button, sensors, and automation logic.
- `coordinator.py`: Handles periodic fetching of the JSON data from the remote server, based on the country and minute selected in the config flow. Uses Home Assistant's DataUpdateCoordinator.
- `config_flow.py`: Provides a UI for users to select their country and the minute past the hour to fetch data. Guesses the country from Home Assistant's locale but allows override.
- `button.py`: Exposes a Home Assistant button entity that lets users manually trigger a data fetch from the UI.
- `sensor.py`: Exposes each top-level key in the fetched JSON as a Home Assistant sensor entity. (To disable, remove/comment out this file and its setup in `__init__.py`.)
- `automation.py`: Contains logic to control devices based on the fetched data. Example: turns an inverter on/off depending on the current electricity price. (You can adapt this logic to your needs.)
- `manifest.json`: Metadata and requirements for the integration (e.g., dependencies like `aiohttp`).
- `README.md`: This documentation file.
- `translations/`: Contains translation files for the integration UI. Home Assistant will use the appropriate language file based on the user's language settings. If a translation is not available, it falls back to `en.json` (English). Provided translations:
  - `en.json`: English (default)
  - `nl.json`: Dutch (Nederlands)
  - `fr.json`: French (Français)
  - `be.json`: Belgian Dutch (Nederlands België)
  - `at.json`: Austrian German (Deutsch Österreich)

  To add more languages, create additional JSON files in this directory following the same structure.

## How It Works
1. **Setup**: User installs the integration (see below). During setup, the user selects their country and the minute past the hour to fetch data.
2. **Data Fetching**: The coordinator fetches the relevant JSON file from the Ampster S3 bucket at the configured time (e.g., 2 minutes past every hour).
3. **Entities**: The integration exposes sensors for each top-level key in the JSON, and a button to manually update the data.
4. **Automation**: The integration can automatically control devices (e.g., turn on/off a switch) based on the fetched data. The example provided uses the current all-in price.

## Installation Instructions

### Option 1: Manual Installation (ZIP or Local Folder)
1. Download this repository as a ZIP file and extract it, or clone the repository.
2. Copy the entire `ampster-integration` folder into your Home Assistant `custom_components` directory (usually at `/config/custom_components/ampster`).
3. Restart Home Assistant.
4. Go to **Settings > Devices & Services > Integrations** and click **Add Integration**. Search for "Ampster" and follow the setup flow.

### Option 2: Install via URL (HACS or Custom Repository)
If you use [HACS](https://hacs.xyz/):
1. In HACS, go to **Integrations > Custom Repositories**.
2. Add the URL of this repository as a custom integration.
3. Install "Ampster" from HACS.
4. Restart Home Assistant and add the integration as above.

> **Note:** If not using HACS, Home Assistant does not support installing custom integrations directly from a URL. You must use the manual method above.

## Customization
- **Country and Minute**: Set during integration setup. Can be changed later via the integration's options.
- **Automation Logic**: Edit `automation.py` to change how devices are controlled based on the data.
- **Sensors**: Edit or remove `sensor.py` if you want to change or disable sensor exposure.

## Requirements
- Home Assistant 2022.0 or newer recommended.
- Python 3.9+ (matches Home Assistant requirements).

## Support
For questions or issues, please open an issue in the repository or consult the Home Assistant developer documentation.

## Tips & Tricks: Accessing JSON Data

The fetched JSON data is available as a Python dictionary via `coordinator.data` in your integration code. Here are some examples:

### Accessing Top-Level Keys
- `country = coordinator.data.get("country")`
- `current_price = coordinator.data.get("current_period_all_in_price")`

### Accessing the `hourly_prices` Array
- `hourly_prices = coordinator.data.get("hourly_prices", [])`

#### Access the 1st element (Python is 0-based):
- `first_hour = hourly_prices[0] if hourly_prices else None`

#### Access the 5th element:
- `fifth_hour = hourly_prices[4] if len(hourly_prices) > 4 else None`

#### Access a specific value inside an element:
- `first_all_in_price = hourly_prices[0]["price"]["all_in_price"] if hourly_prices else None`
- `fifth_period = hourly_prices[4]["period"] if len(hourly_prices) > 4 else None`

### Iterating Over All Hourly Prices
```python
for hour in hourly_prices:
    period = hour["period"]
    all_in_price = hour["price"]["all_in_price"]
    # Do something with period and all_in_price
```

### Checking the Length of an Array
- To check if there are 12 elements in the `hourly_prices` array:
```python
hourly_prices = coordinator.data.get("hourly_prices", [])
if len(hourly_prices) == 12:
    # There are exactly 12 elements
    ...
else:
    # There are not 12 elements
    ...
```

### Defensive Access
Always check for existence and length before accessing array elements to avoid `IndexError`.

## Accessing Exposed Data in Home Assistant

When this integration is installed, it creates sensor entities in Home Assistant for each top-level key in the fetched JSON. These sensors can be used in automations, dashboards (Lovelace), scripts, and templates just like any other Home Assistant entity.

### Example Sensor Entity IDs
- `sensor.ampster_current_period_all_in_price`
- `sensor.ampster_country`
- `sensor.ampster_currency`

The exact entity IDs will be based on the key names in the JSON and may be prefixed with `sensor.ampster_`.

### Using the Data in Automations
You can use these sensors in Home Assistant automations. For example, to trigger an action when the current all-in price drops below 0.20 EUR/kWh:

```yaml
automation:
  - alias: 'Turn on inverter when price is low'
    trigger:
      - platform: numeric_state
        entity_id: sensor.ampster_current_period_all_in_price
        below: 0.20
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.inverter
```

### Using the Data in Dashboards
Add the sensors to your Lovelace dashboard as you would any other sensor:

```yaml
entities:
  - entity: sensor.ampster_current_period_all_in_price
  - entity: sensor.ampster_country
```

### Using the Data in Templates
You can access the sensor values in Home Assistant templates:

```jinja
{{ states('sensor.ampster_current_period_all_in_price') }}
```

## Default Configuration and Where to Change It

- **Base URL for Data Fetching**: The default base URL for fetching electricity price data is set in `coordinator.py`:
  - `self.url = url or f"https://ampster.s3.us-east-1.amazonaws.com/electricity_prices/{self.country_prefix}.json"`
  - You can change the base URL by editing this line in `coordinator.py` if you want to use a different data source.

- **Default Country and Minute (Cron Time)**:
  - The default country is guessed from your Home Assistant locale in both `config_flow.py` (for the UI default) and `coordinator.py` (for fallback logic).
  - The default minute past the hour to fetch data is set to `2` in both `config_flow.py` and `coordinator.py`.
  - Users can override these defaults during the integration setup in the Home Assistant UI.

- **Changing Defaults**:
  - To change the default country or minute for all new users, edit the default values in `config_flow.py`.
  - To change the fallback logic or base URL, edit `coordinator.py`.

- **User Configuration**:
  - During setup, users can select their country and the minute past the hour to fetch data. These settings are stored in the integration's config entry and used by the coordinator.

## Branding (Logo & Icon)

To add custom branding to your integration in the Home Assistant UI:
- Place your images in the `.branding/` directory in this integration folder.
- Required files:
  - `logo.png` (recommended size: 256x256 px, transparent background)
  - `icon.png` (recommended size: 32x32 px, transparent background)
- Home Assistant will use these images in the integrations list and on the integration card.
- For more details, see: https://developers.home-assistant.io/docs/integration_custom_branding/

If these images are not provided, Home Assistant will display a default puzzle piece icon for your integration.
