import os
import time
import requests
from datetime import datetime
import sys

# Add parent directory to path to allow importing logger module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import logger

IMAGE_URL = "http://192.168.0.195/240x240.jpg"  # Need to Modify according to your own ESP32 CAM IP

def fetch_image(label=None):
    try:
        logger.info(f"Fetching image from {IMAGE_URL}")
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
            logger.info(f"Image saved as {filename}")
        else:
            logger.error(f"Failed to fetch image. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching image: {e}")

def fetch_and_overwrite_image(label=None, filename="latest.jpg"):
    """Fetch image and overwrite the same file each time."""
    try:
        logger.info(f"Fetching and overwriting image from {IMAGE_URL}")
        response = requests.get(IMAGE_URL, timeout=5)
        if response.status_code == 200:
            folder = "data"
            if label:
                folder = os.path.join(folder, label)
            os.makedirs(folder, exist_ok=True)

            full_path = os.path.join(folder, filename)
            with open(full_path, 'wb') as f:
                f.write(response.content)
            logger.info(f"Image overwritten as {full_path}")
        else:
            logger.error(f"Failed to fetch image. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching image: {e}")

# Example usage:
if __name__ == "__main__":
    fetch_image("unhealthy")          # Saves in data/unhealthy
    #fetch_image("unhealthy")        # Saves in data/unhealthy
    #fetch_and_overwrite_image("healthy")   # Overwrites latest.jpg in data/healthy
