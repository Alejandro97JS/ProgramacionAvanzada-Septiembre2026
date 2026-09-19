import requests
import json

BASE_URL = "https://api.open-meteo.com/v1/forecast"

# Cities with their coordinates (latitude, longitude)
CITIES = {
    "Madrid":    {"lat": 40.42, "lon": -3.70},
    "Barcelona": {"lat": 41.39, "lon": 2.17},
    "London":    {"lat": 51.51, "lon": -0.13},
    "Paris":     {"lat": 48.86, "lon": 2.35},
    "Berlin":    {"lat": 52.52, "lon": 13.41},
    "Rome":      {"lat": 41.90, "lon": 12.50},
}

try:
    params = {
        "latitude": CITIES["Barcelona"].get("lat"),
        "longitude": CITIES["Madrid"].get("lon")
    }
    response = requests.get(BASE_URL, params)
    response.raise_for_status()
    print(response.status_code)
except requests.exceptions.RequestException as e:
    print("Something failed: ", e)
    exit()

data = response.json()
print(json.dumps(data, indent=4))

