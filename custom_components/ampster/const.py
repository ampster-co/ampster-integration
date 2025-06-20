"""Constants for Ampster integration."""
DOMAIN = "ampster"

# Default values
DEFAULT_COUNTRY = "NL"
DEFAULT_MINUTE = 5
DEFAULT_BASE_URL = "https://ampster.s3.us-east-1.amazonaws.com/electricity_prices/"

# Upload configuration defaults
DEFAULT_UPLOAD_URL = "https://yv3l9alv8g.execute-api.us-east-1.amazonaws.com/prod/data"
DEFAULT_UPLOAD_INTERVAL = 15
DEFAULT_UPLOAD_SENSORS = ""
DEFAULT_API_KEY = ""

# For backward compatibility, provide BASE_URL as an alias for DEFAULT_BASE_URL
BASE_URL = DEFAULT_BASE_URL

# Supported countries
SUPPORTED_COUNTRIES = ["NL", "FR", "BE", "AT"]
