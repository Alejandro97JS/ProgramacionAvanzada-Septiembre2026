from sys import exception
import requests
import json

from urllib3 import response

# url = "https://api.open-meteo.com/v1/forecast"
# coordinates_path = "?latitude=41.7252&longitude=1.8264"
#
# result = requests.get(url+coordinates_path+"&current_weather=true"+"&forecast_days=10")
# if result.status_code != 200:
#     print(f"Error: {result.status_code}")
#     exit()
#
# print(result.json())
#
# weather_data = result.json()
# print("\n\nWeather data:", json.dumps(weather_data, indent=4))
# current_weather = weather_data["current_weather"]
# print(json.dumps(current_weather, indent=4))

def print_separator(func):
    def wrapper(*args, **kwargs):
        print("\n" + "-"*40 + "\n")
        result = func(*args, **kwargs)
        print("\n" + "-"*40 + "\n")
        return result
    return wrapper


def test_1():
    url = "https://jsonplaceholder.typicode.com/posts/1"

    response = requests.get(url)

    print("status code:", f"status code: {response.status_code}" + "\n"*2)
    print("headers:", f"{json.dumps(dict(response.headers), indent=4)}" + "\n"*2)

    data = response.json()
    print("data:", f"{json.dumps(data, indent=4)}" + "\n"*2)


@print_separator
def test_2():
    url = "http://reqres.in/api/users"
    params = {
        "page": 2,
    }

    response = requests.get(url, params=params)

    data = response.json()
    
    print(f"Data es del tipo {type(data)}. Estos son los datos:" + "\n"*2 +f"{json.dumps(data, indent=4)}")

    print_separator(func=None)

    print("Users list:")

    for user in data["data"]:
        name = user.get("first_name","--")
        email = user.get("email","--")

        print(f"    name: {name} | email: {email}")

@print_separator
def test_3():
    try:
        url = "http://reqres.in/apisss/user"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as e:
        print("something fail: ", e)



test_3()