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

---

## Accessing Ampster Data in Home Assistant Templates

The Ampster integration exposes data as Home Assistant sensor entities (e.g., `sensor.ampster_country`). You can use these sensors in automations, dashboards, scripts, and templates.

### Accessing Sensor Values in Templates

To get the value of a sensor in a template, use:

```jinja
{{ states('sensor.ampster_country') }}
```

This returns the current value (state) of the `sensor.ampster_country` entity as a string.

### Accessing Sensor Attributes

If your sensor exposes additional attributes (such as a dictionary or list), use:

```jinja
{{ state_attr('sensor.ampster_country', 'full_value') }}
```

Replace `'full_value'` with the attribute name you want to access.

### Example Usage in Automations

You can use these sensors in Home Assistant automations. For example:

```yaml
automation:
  - alias: 'Notify country change'
    trigger:
      - platform: state
        entity_id: sensor.ampster_country
    action:
      - service: notify.notify
        data:
          message: "Ampster country changed to {{ states('sensor.ampster_country') }}"
```

### Example Usage in Lovelace Dashboards

Add the sensor to an entities card:

```yaml
entities:
  - entity: sensor.ampster_country
```

### Troubleshooting
- If you see `unknown` or `unavailable`, the entity may not be initialized yet or there may be a data issue.
- Use Developer Tools → States in Home Assistant to see all available entities and their current values.

---

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

## Automating Commit, Tag, and GitHub Release from the CLI

You can automate the process of committing, tagging, and creating a GitHub release for this integration using the command line.

### 1. Commit and Tag (Standard Git)

```zsh
git add .
git commit -m "Your commit message"
git push origin main
git tag vX.Y.Z
git push origin vX.Y.Z
```
Replace `vX.Y.Z` with your desired version number (e.g., `v1.0.9`).

### 2. Create a GitHub Release via CLI

#### Option A: Using the GitHub CLI (`gh`)
If you have the [GitHub CLI](https://cli.github.com/) (`gh`) installed, you can create a release with:

```zsh
gh release create vX.Y.Z --title "vX.Y.Z" --notes "Describe your changes here"
```
This will create a release for tag `vX.Y.Z` with the given title and notes.

#### Option B: Using cURL (GitHub API)
If you don’t have `gh`, you can use the GitHub API with `curl` (requires a GitHub token):

```zsh
curl -X POST \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -d '{"tag_name": "vX.Y.Z", "name": "vX.Y.Z", "body": "Describe your changes here", "draft": false, "prerelease": false}' \
  https://api.github.com/repos/alexhowarth/ampster-integration/releases
```
Replace `YOUR_GITHUB_TOKEN` with a personal access token.

---

**Summary:**
- Use `git` for commit and tag.
- Use `gh release create ...` for a release (recommended).
- You can script all of this for full automation!

## HACS: Only Tagged Releases Are Available

When using HACS (Home Assistant Community Store) to install this integration, only versions that have both a git tag and a published GitHub release are available for installation or update. Commits on the main branch or untagged code will not appear in HACS.

**To make a new version available in HACS:**
1. Commit and push your changes to the main branch.
2. Create a new git tag (e.g., `v1.0.9`) and push it to GitHub.
3. Create a GitHub release for that tag (see the section above on automating this process).
4. HACS will detect the new release and make it available for installation or update.

If you do not see your latest changes in HACS, ensure you have created both a tag and a release for your desired version.

## Enabling Debug Logging for the Integration

To see detailed logs for the Ampster integration, you can enable debug logging in Home Assistant. This is useful for troubleshooting and development.

### Steps to Enable Debug Logging

1. **Edit `configuration.yaml`:**
   - Open `configuration.yaml` (usually found in the root of your Home Assistant config folder).
   - Add the following section at the end of the file:
     ```yaml
     logger:
       default: info
       logs:
         custom_components.ampster: debug
     ```
   - Save the file.

2. **Restart Home Assistant:**
   - Go to **Settings → System → Restart** to apply the changes.

After restarting, detailed debug logs for the Ampster integration will appear in your Home Assistant logs. This will help you see when data is fetched, configuration details, and any issues that arise.

> **Tip:** You can use the [File Editor add-on](https://www.home-assistant.io/integrations/file_editor/) to edit `configuration.yaml` directly from the Home Assistant UI.

## Manual Update Button: Where to Find It

When the Ampster integration is installed, it creates a manual update button entity in Home Assistant. This button allows you to trigger a data fetch on demand, outside of the scheduled updates.

To find and use the manual update button:

1. Go to **Settings → Devices & Services** in the Home Assistant UI.
2. Click on the **Entities** tab at the top of the page.
3. In the search bar, type `ampster` to filter all Ampster-related entities.
4. Look for an entity named something like `button.ampster_update` (the exact name may vary depending on your setup).
5. Click the button entity to open its details. You can then press the button directly from the UI to manually trigger a data update.

You can also add this button to your dashboard for quick access, or use it in automations and scripts.

---

## Developing with the Home Assistant VS Code Add-on

For the fastest development workflow, use the Visual Studio Code (VS Code) add-on in Home Assistant. This allows you to edit your integration files directly in the Home Assistant environment and reload changes instantly.

### Steps:

1. **Install the VS Code Add-on:**
   - In Home Assistant, go to **Settings → Add-ons → Add-on Store**.
   - Search for "VS Code" or "Visual Studio Code" and install it.
   - Start the add-on and open it from the sidebar.

2. **Open Your Integration Folder:**
   - In the VS Code add-on, navigate to `/config/custom_components/ampster/`.
   - Edit your Python files directly here. Changes are saved immediately in your Home Assistant environment.

3. **Reload the Integration:**
   - After saving changes, go to **Settings → Devices & Services → Integrations → Ampster → ... (menu) → Reload**.
   - This reloads your integration without restarting Home Assistant. (A full restart is only needed if you change dependencies or `manifest.json`.)

4. **Use Logging for Debugging:**
   - Add `import logging` and use `_LOGGER.debug(...)` in your code.
   - Enable debug logging as described in the Debug Logging section above.
   - View logs in **Developer Tools → Logs** in the Home Assistant UI.

**Tip:** You can also use the VS Code add-on to edit `configuration.yaml` and other Home Assistant files.

---

## Local Testing & Development Requirements

To run and develop tests for this integration locally, you need to install the development requirements and the Home Assistant package.

### 1. Install Development Requirements

In your project root, run:

```zsh
pip install -r requirements-dev.txt
```

This will install `pytest`, `pytest-asyncio`, and `aiohttp` for running and writing tests.

### 2. Install Home Assistant Package (Required for Tests)

The test suite imports Home Assistant modules. You must install the `homeassistant` package in your environment:

```zsh
pip install homeassistant
```

If you see an error like `ModuleNotFoundError: No module named "homeassistant"`, this step is required.

### 3. Running Tests

To run all tests:

```zsh
pytest tests/
```

This will execute all test files in the `tests/` directory.

---

## Integration Branding (Logo & Icon in Home Assistant UI)

To have your integration's logo and icon appear in the Home Assistant user interface (e.g., in the integrations list and on the integration card), you need to submit your branding assets to the official Home Assistant Brands repository.

The `.branding/` folder method within the custom component directory is **not** used for custom integration branding.

### Process for Submitting Branding:

1.  **Prepare Your Assets:**
    *   **`logo.png`**: A 512x512 pixel PNG image, ideally with a transparent background. This is the main logo for your integration.
    *   **`icon.png`**: A 146x146 pixel PNG image, also ideally with a transparent background. This icon is used in smaller UI elements. The Home Assistant team might have specific guidelines or tools for generating the icon from your logo to ensure it fits the safe zone.

2.  **Fork the Repository:**
    *   Go to the [Home Assistant Brands GitHub repository](https://github.com/home-assistant/brands) and fork it to your own GitHub account.

3.  **Add Your Branding Files:**
    *   In your forked repository, navigate to the `custom_integrations/` directory.
    *   Create a new folder named after your integration's domain. For this integration, the domain is `ampster`. So, you would create `custom_integrations/ampster/`.
    *   Place your `logo.png` and `icon.png` files inside this `custom_integrations/ampster/` directory.

4.  **(Optional) Add `brand.json`:**
    *   If your integration has specific product names or connects to a cloud service that has distinct branding, you might need to add a `brand.json` file in the same `custom_integrations/ampster/` directory. This file provides metadata about your brand.
    *   Example `brand.json`:
        ```json
        {
          "name": "Ampster",
          "domain": "ampster",
          "integrations": {
            "ampster": [
              "https://www.example.com" // Link to your product/service if applicable
            ]
          }
        }
        ```
        Consult the `home-assistant/brands` repository's `README` or contribution guidelines for the exact structure and requirements for `brand.json`.

5.  **Submit a Pull Request (PR):**
    *   Commit your changes (the new folder and image files) to your forked repository.
    *   Go back to the original [Home Assistant Brands GitHub repository](https://github.com/home-assistant/brands) and create a new Pull Request from your fork.
    *   Clearly describe your integration and the branding you are adding.

6.  **Review and Merge:**
    *   The Home Assistant team will review your PR. They might request changes to your images or `brand.json` to meet their guidelines.
    *   Once approved, your PR will be merged.

7.  **Branding Appears in Home Assistant:**
    *   After your branding is merged into the `home-assistant/brands` repository, it will be included in a future Home Assistant release. Users will then see your logo and icon in their Home Assistant UI when they use your integration.

**Important Notes:**
*   Always check the latest contribution guidelines in the `home-assistant/brands` repository, as the process or requirements might change.
*   The `.branding/` directory that might have been mentioned in older documentation or for different purposes should be removed from your `custom_components/ampster/` directory as it is not used for this type of branding.
