import requests
from PIL import Image
from io import BytesIO

def get_random_dog_image():
    url = "https://dog.ceo/api/breeds/image/random"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "success":
            return data["message"]
        else:
            print("Failed to fetch dog image.")
            return None
    except requests.RequestException as e:
        print(f"Error fetching dog image: {e}")
        return None

def display_image_from_url(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        img.show()
    except requests.RequestException as e:
        print(f"Error fetching image: {e}")


def main():
    print("🔹 Dog CEO API Test 🔹\n")
    image_url = get_random_dog_image()
    if image_url:
        print(f"🐶 Random Dog Image: {image_url}\n")
        display_image_from_url(image_url)

if __name__ == "__main__":
    main()
