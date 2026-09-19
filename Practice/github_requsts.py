import json
import os

from openai import timeout
import requests

token = os.environ["GITHUB_DAVID_TOKEN"]
# token = "djdjdj" # usar para test de excepción

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}

base_url = "https://api.github.com/user"


try:
    response = requests.get(base_url,headers=headers,timeout=5)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(e)
    exit()

data = response.json()

user = data.get("login")
email = data.get("email")
location = data.get("location")
print("\n"+f"{json.dumps(data, indent=4)}" + "\n"*4)
print("Usuario:", user)
print("Email:", email)
print("Repositorios públicos:", data["public_repos"])

try:
    repo_response = requests.get(data.get("repos_url"))
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(e)
    exit()

data = repo_response.json()
print("Repos list: \n", json.dumps(data, indent=4))