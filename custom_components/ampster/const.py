"""Constants for Ampster integration."""
DOMAIN = "ampster"

# Default values
DEFAULT_COUNTRY = "NL"
DEFAULT_MINUTE = 5
DEFAULT_BASE_URL = "https://ampster.s3.us-east-1.amazonaws.com/electricity_prices/"

# For backward compatibility, provide BASE_URL as an alias for DEFAULT_BASE_URL
BASE_URL = DEFAULT_BASE_URL

# Supported countries
SUPPORTED_COUNTRIES = ["NL", "FR", "BE", "AT"]
