import requests
import json

url = "https://api.open-meteo.com/v1/forecast"
coordinates_path = "?latitude=41.7252&longitude=1.8264"

result = requests.get(url+coordinates_path+"&current_weather=true"+"&forecast_days=10")
if result.status_code != 200:
    print(f"Error: {result.status_code}")
    exit()

print(result.json())

weather_data = result.json()
print("\n\nWeather data:", json.dumps(weather_data, indent=4))
current_weather = weather_data["current_weather"]
print(json.dumps(current_weather, indent=4))

