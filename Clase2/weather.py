"""
https://api.open-meteo.com/v1/forecast

This script makes several calls to the Open-Meteo API to:
1. Get the current weather for several European cities
2. Compare temperatures across cities
3. Get the 7-day forecast and compute weekly averages
4. Determine the warmest and coldest city
5. Calculate the average weekly rain probability
"""

import requests

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


def get_current_weather(name: str, lat: float, lon: float) -> dict:
    """Get the current weather conditions for a city."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        "timezone": "auto",
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()
    current = data["current"]
    return {
        "city": name,
        "temperature": current["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "wind_kmh": current["wind_speed_10m"],
        "weather_code": current["weather_code"],
    }


def get_weekly_forecast(name: str, lat: float, lon: float) -> dict:
    """Get the 7-day daily forecast for a city."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "auto",
        "forecast_days": 7,
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()
    daily = data["daily"]
    return {
        "city": name,
        "dates": daily["time"],
        "temp_max": daily["temperature_2m_max"],
        "temp_min": daily["temperature_2m_min"],
        "rain_prob": daily["precipitation_probability_max"],
    }


def interpret_weather_code(code: int) -> str:
    """Translate a WMO weather_code into a human-readable description."""
    descriptions = {
        0: "Clear sky ☀️",
        1: "Mainly clear 🌤️",
        2: "Partly cloudy ⛅",
        3: "Overcast ☁️",
        45: "Fog 🌫️",
        48: "Depositing rime fog 🌫️❄️",
        51: "Light drizzle 🌦️",
        53: "Moderate drizzle 🌦️",
        55: "Dense drizzle 🌧️",
        61: "Light rain 🌧️",
        63: "Moderate rain 🌧️",
        65: "Heavy rain 🌧️🌧️",
        71: "Light snow 🌨️",
        73: "Moderate snow 🌨️",
        75: "Heavy snow ❄️❄️",
        80: "Light showers 🌦️",
        81: "Moderate showers 🌧️",
        82: "Violent showers ⛈️",
        95: "Thunderstorm ⛈️",
        96: "Thunderstorm with hail ⛈️🧊",
        99: "Severe thunderstorm with hail ⛈️🧊",
    }
    return descriptions.get(code, f"Unknown code ({code})")


# ---------------------------------------------------------------------------
# 1. Current weather in all cities
# ---------------------------------------------------------------------------
print("=" * 60)
print("  CURRENT WEATHER IN EUROPEAN CITIES")
print("=" * 60)

current_data = []
for city, coords in CITIES.items():
    info = get_current_weather(city, coords["lat"], coords["lon"])
    current_data.append(info)
    status = interpret_weather_code(info["weather_code"])
    print(f"\n📍 {info['city']}:")
    print(f"   Temperature: {info['temperature']} °C")
    print(f"   Humidity:    {info['humidity']} %")
    print(f"   Wind:        {info['wind_kmh']} km/h")
    print(f"   Condition:   {status}")

# ---------------------------------------------------------------------------
# 2. Temperature ranking
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("  TEMPERATURE RANKING (warmest to coldest)")
print("=" * 60)

ranking = sorted(current_data, key=lambda x: x["temperature"], reverse=True)
for i, info in enumerate(ranking, start=1):
    print(f"  {i}. {info['city']:12s} → {info['temperature']:5.1f} °C")

difference = ranking[0]["temperature"] - ranking[-1]["temperature"]
print(f"\n  Difference between warmest and coldest: {difference:.1f} °C")

# ---------------------------------------------------------------------------
# 3. Weekly forecast and average temperatures
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("  WEEKLY FORECAST — AVERAGE TEMPERATURES")
print("=" * 60)

forecasts = []
for city, coords in CITIES.items():
    fc = get_weekly_forecast(city, coords["lat"], coords["lon"])
    forecasts.append(fc)

weekly_averages = []
for fc in forecasts:
    avg_max = sum(fc["temp_max"]) / len(fc["temp_max"])
    avg_min = sum(fc["temp_min"]) / len(fc["temp_min"])
    avg_overall = (avg_max + avg_min) / 2
    avg_rain = sum(fc["rain_prob"]) / len(fc["rain_prob"])
    weekly_averages.append({
        "city": fc["city"],
        "avg_max": avg_max,
        "avg_min": avg_min,
        "avg_overall": avg_overall,
        "avg_rain": avg_rain,
    })
    print(f"\n📍 {fc['city']}:")
    print(f"   Avg. max temp: {avg_max:5.1f} °C")
    print(f"   Avg. min temp: {avg_min:5.1f} °C")
    print(f"   Avg. temp:     {avg_overall:5.1f} °C")
    print(f"   Avg. rain prob: {avg_rain:4.0f} %")

# ---------------------------------------------------------------------------
# 4. Warmest and coldest city of the week
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("  WEEKLY SUMMARY")
print("=" * 60)

warmest = max(weekly_averages, key=lambda x: x["avg_overall"])
coldest = min(weekly_averages, key=lambda x: x["avg_overall"])
rainiest = max(weekly_averages, key=lambda x: x["avg_rain"])
driest = min(weekly_averages, key=lambda x: x["avg_rain"])

print(f"  🔥 Warmest city this week:   {warmest['city']} ({warmest['avg_overall']:.1f} °C)")
print(f"  🥶 Coldest city this week:   {coldest['city']} ({coldest['avg_overall']:.1f} °C)")
print(f"  🌧️  Rainiest city this week:  {rainiest['city']} ({rainiest['avg_rain']:.0f} % avg. prob.)")
print(f"  ☀️  Driest city this week:    {driest['city']} ({driest['avg_rain']:.0f} % avg. prob.)")

# ---------------------------------------------------------------------------
# 5. Day-by-day detail for the warmest city
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print(f"  DAY-BY-DAY DETAIL — {warmest['city'].upper()}")
print("=" * 60)

fc_warmest = next(f for f in forecasts if f["city"] == warmest["city"])
print(f"  {'Date':<12} {'Max (°C)':>9} {'Min (°C)':>9} {'Rain (%)':>10}")
print(f"  {'-'*12} {'-'*9} {'-'*9} {'-'*10}")
for date, tmax, tmin, rain in zip(
    fc_warmest["dates"],
    fc_warmest["temp_max"],
    fc_warmest["temp_min"],
    fc_warmest["rain_prob"],
):
    print(f"  {date:<12} {tmax:>8.1f}  {tmin:>8.1f}  {rain:>8.0f} %")

print("\n✅ All API calls completed successfully.")
