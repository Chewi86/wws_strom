"""Konstanten für die WestfalenWIND Strom Integration."""

DOMAIN = "wws_strom"

API_URL = "https://api.wws.tarifdynamik.de"
AUTH_ENDPOINT = f"{API_URL}/tokens/"
PRICES_ENDPOINT = f"{API_URL}/public/energyprices/latest"
HISTORIC_PRICES_ENDPOINT = f"{API_URL}/public/energyprices"
MEASUREMENTS_ENDPOINT = f"{API_URL}/public/measurements/"

CONF_USERNAME = "username"
CONF_PASSWORD = "password"

DEFAULT_NAME = "WWS Strompreis"
DEFAULT_SCAN_INTERVAL = 3600  # Alle 60 Minuten (oder 15 min im Coordinator)