import os
import time
import requests
from datetime import datetime

IMAGE_URL = "http://192.168.0.187/240x240.jpg"          # Need to Modify according to your own ESP32 CAM IP

def fetch_image(label=None):
    try:
        response = requests.get(IMAGE_URL, timeout=5)
        if response.status_code == 200:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder = "data"
            if label:
                folder = os.path.join(folder, label)
            os.makedirs(folder, exist_ok=True)

            filename = os.path.join(folder, f"esp32_image_{timestamp}.jpg")
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"Image saved as {filename}")
        else:
            print(f"Failed to fetch image. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image: {e}")

def fetch_and_overwrite_image(label=None, filename="latest.jpg"):
    """Fetch image and overwrite the same file each time."""
    try:
        response = requests.get(IMAGE_URL, timeout=5)
        if response.status_code == 200:
            folder = "data"
            if label:
                folder = os.path.join(folder, label)
            os.makedirs(folder, exist_ok=True)

            full_path = os.path.join(folder, filename)
            with open(full_path, 'wb') as f:
                f.write(response.content)
            print(f"Image overwritten as {full_path}")
        else:
            print(f"Failed to fetch image. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image: {e}")

# Example usage:
fetch_image("unhealthy")          # Saves in data/healthy
#fetch_image("unhealthy")        # Saves in data/unhealthy
#fetch_and_overwrite_image("healthy")   # Overwrites latest.jpg in data/healthy
