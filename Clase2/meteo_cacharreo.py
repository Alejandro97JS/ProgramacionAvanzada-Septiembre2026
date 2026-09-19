"""
https://api.open-meteo.com/v1/forecast

Cacharreo con Open-Meteo (punto 1 de apis_to_use.md).
Prueba filtros distintos a weather.py:
1. Tiempo actual + sensación térmica y UV
2. Pronóstico horario (próximas horas)
3. Amanecer / atardecer y horas de luz
4. Comparar hoy vs hace 7 días (past_days)
5. Índice de "día agradable" entre ciudades
6. Clima en N días para una ciudad concreta
"""

import requests

BASE_URL = "https://api.open-meteo.com/v1/forecast"

CITIES = {
    "Madrid":     {"lat": 40.42, "lon": -3.70},
    "Valencia":   {"lat": 39.47, "lon": -0.38},
    "Sevilla":    {"lat": 37.39, "lon": -5.99},
    "Bilbao":     {"lat": 43.26, "lon": -2.93},
    "Barcelona":  {"lat": 41.39, "lon": 2.17},
}


def get_current_extended(name: str, lat: float, lon: float) -> dict:
    """Tiempo actual con más variables: sensación térmica y UV."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": (
            "temperature_2m,apparent_temperature,"
            "relative_humidity_2m,uv_index,weather_code,is_day"
        ),
        "timezone": "auto",
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    current = response.json()["current"]
    return {
        "city": name,
        "temperature": current["temperature_2m"],
        "feels_like": current["apparent_temperature"],
        "humidity": current["relative_humidity_2m"],
        "uv": current["uv_index"],
        "weather_code": current["weather_code"],
        "is_day": bool(current["is_day"]),
    }


def get_hourly_next_hours(name: str, lat: float, lon: float, hours: int = 6) -> dict:
    """Pronóstico horario: temperatura y probabilidad de lluvia."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,precipitation_probability,weather_code",
        "forecast_hours": hours,
        "timezone": "auto",
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    hourly = response.json()["hourly"]
    return {
        "city": name,
        "times": hourly["time"][:hours],
        "temps": hourly["temperature_2m"][:hours],
        "rain_prob": hourly["precipitation_probability"][:hours],
        "codes": hourly["weather_code"][:hours],
    }


def get_sun_times(name: str, lat: float, lon: float) -> dict:
    """Amanecer, atardecer y duración del día (daily)."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "sunrise,sunset,daylight_duration,sunshine_duration",
        "forecast_days": 1,
        "timezone": "auto",
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    daily = response.json()["daily"]
    return {
        "city": name,
        "sunrise": daily["sunrise"][0],
        "sunset": daily["sunset"][0],
        "daylight_sec": daily["daylight_duration"][0],
        "sunshine_sec": daily["sunshine_duration"][0],
    }


def get_today_vs_week_ago(name: str, lat: float, lon: float) -> dict:
    """Compara la temp máxima de hoy con la de hace 7 días."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min",
        "past_days": 7,
        "forecast_days": 1,
        "timezone": "auto",
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    daily = response.json()["daily"]
    # Índice 0 = hace 7 días, índice -1 = hoy
    return {
        "city": name,
        "dates": daily["time"],
        "max_week_ago": daily["temperature_2m_max"][0],
        "min_week_ago": daily["temperature_2m_min"][0],
        "max_today": daily["temperature_2m_max"][-1],
        "min_today": daily["temperature_2m_min"][-1],
    }


def get_weather_in_days(city: str, days: int = 10) -> dict:
    """
    Pronóstico para una ciudad dentro de `days` días.

    Ejemplo: get_weather_in_days("Madrid", 10) → clima dentro de 10 días.
    La ciudad debe estar en CITIES. Open-Meteo admite hasta 16 días.
    """
    if city not in CITIES:
        raise ValueError(f"Ciudad desconocida: {city}. Disponibles: {list(CITIES)}")
    if not 1 <= days <= 16:
        raise ValueError("days debe estar entre 1 y 16")

    coords = CITIES[city]
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "daily": (
            "temperature_2m_max,temperature_2m_min,"
            "precipitation_probability_max,weather_code,precipitation_sum"
        ),
        "forecast_days": days + 1,  # índice 0 = hoy → necesitamos days+1 entradas
        "timezone": "auto",
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    daily = response.json()["daily"]
    i = days  # día N desde hoy

    return {
        "city": city,
        "days_ahead": days,
        "date": daily["time"][i],
        "temp_max": daily["temperature_2m_max"][i],
        "temp_min": daily["temperature_2m_min"][i],
        "rain_prob": daily["precipitation_probability_max"][i],
        "rain_mm": daily["precipitation_sum"][i],
        "weather_code": daily["weather_code"][i],
        "condition": interpret_weather_code(daily["weather_code"][i]),
    }


def interpret_weather_code(code: int) -> str:
    descriptions = {
        0: "Despejado",
        1: "Mayormente despejado",
        2: "Parcialmente nublado",
        3: "Cubierto",
        45: "Niebla",
        61: "Lluvia ligera",
        63: "Lluvia",
        65: "Lluvia intensa",
        80: "Chubascos",
        95: "Tormenta",
    }
    return descriptions.get(code, f"Código {code}")


def comfort_score(info: dict) -> float:
    """
    Puntuación casera de 'día agradable' (0-100).
    Premia ~22 °C de sensación térmica, humedad media y UV moderado.
    """
    temp_penalty = abs(info["feels_like"] - 22) * 3
    humidity_penalty = abs(info["humidity"] - 50) * 0.4
    uv_penalty = max(0, info["uv"] - 6) * 4
    score = 100 - temp_penalty - humidity_penalty - uv_penalty
    return max(0.0, min(100.0, score))


# ---------------------------------------------------------------------------
# 1. Tiempo actual ampliado
# ---------------------------------------------------------------------------
print("=" * 60)
print("  TIEMPO ACTUAL (sensación térmica + UV)")
print("=" * 60)

current_data = []
for city, coords in CITIES.items():
    info = get_current_extended(city, coords["lat"], coords["lon"])
    current_data.append(info)
    moment = "de día" if info["is_day"] else "de noche"
    print(f"\n📍 {info['city']} ({moment}):")
    print(f"   Temp:        {info['temperature']:.1f} °C")
    print(f"   Sensación:   {info['feels_like']:.1f} °C")
    print(f"   Humedad:     {info['humidity']} %")
    print(f"   UV:          {info['uv']:.1f}")
    print(f"   Condición:   {interpret_weather_code(info['weather_code'])}")

# ---------------------------------------------------------------------------
# 2. Índice de confort
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("  RANKING 'DÍA AGRADABLE'")
print("=" * 60)

ranked = sorted(current_data, key=comfort_score, reverse=True)
for i, info in enumerate(ranked, start=1):
    score = comfort_score(info)
    print(f"  {i}. {info['city']:12s} → {score:5.1f}/100  "
          f"(sensación {info['feels_like']:.1f} °C)")

# ---------------------------------------------------------------------------
# 3. Pronóstico horario de la ciudad más agradable
# ---------------------------------------------------------------------------
best = ranked[0]
print("\n" + "=" * 60)
print(f"  PRÓXIMAS 6 HORAS — {best['city'].upper()}")
print("=" * 60)

coords = CITIES[best["city"]]
hourly = get_hourly_next_hours(best["city"], coords["lat"], coords["lon"], hours=6)
print(f"  {'Hora':<18} {'Temp':>7} {'Lluvia':>8}  Condición")
print(f"  {'-'*18} {'-'*7} {'-'*8}  {'-'*20}")
for t, temp, rain, code in zip(
    hourly["times"], hourly["temps"], hourly["rain_prob"], hourly["codes"]
):
    hour = t.replace("T", " ")
    print(f"  {hour:<18} {temp:>6.1f}°  {rain:>6.0f} %  {interpret_weather_code(code)}")

# ---------------------------------------------------------------------------
# 4. Amanecer / atardecer
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("  AMANECER / ATARDECER HOY")
print("=" * 60)

for city, coords in CITIES.items():
    sun = get_sun_times(city, coords["lat"], coords["lon"])
    daylight_h = sun["daylight_sec"] / 3600
    sunshine_h = sun["sunshine_sec"] / 3600
    print(f"\n📍 {sun['city']}:")
    print(f"   Amanece:     {sun['sunrise'].replace('T', ' ')}")
    print(f"   Anochece:    {sun['sunset'].replace('T', ' ')}")
    print(f"   Horas de luz: {daylight_h:.1f} h  |  Sol efectivo: {sunshine_h:.1f} h")

# ---------------------------------------------------------------------------
# 5. Hoy vs hace una semana
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("  HOY vs HACE 7 DÍAS (temp máxima)")
print("=" * 60)

for city, coords in CITIES.items():
    cmp = get_today_vs_week_ago(city, coords["lat"], coords["lon"])
    delta = cmp["max_today"] - cmp["max_week_ago"]
    arrow = "🔥" if delta > 0 else "❄️" if delta < 0 else "➡️"
    print(
        f"  {cmp['city']:12s}  "
        f"hace 7d: {cmp['max_week_ago']:5.1f} °C  |  "
        f"hoy: {cmp['max_today']:5.1f} °C  |  "
        f"Δ {delta:+.1f} °C {arrow}"
    )

def clima_en_dias(ciudad: str, dias: int = 10) -> dict:
    """
    Recibe una ciudad y el número de días; retorna el clima previsto ese día.

    Ejemplo:
        clima_en_dias("Madrid", 10)
    """
    return get_weather_in_days(ciudad, days=dias)


# Ejemplo de uso
print(clima_en_dias("Madrid", 10))
print("\n✅ Cacharreo con Open-Meteo completado.")
