import os

import requests

from config.config import GENDER_DETECTION_API_URL, GENDER_DETECTION_BEARER_TOKEN

headers = {
    "Authorization": f"Bearer {GENDER_DETECTION_BEARER_TOKEN}"
}


# Takes the filename of the audio with the voice
# Returns the voice gender ('female' or 'male'), str type

def voice_gender_detection(filename):
    try:
        with open(filename, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return None

    response = requests.post(GENDER_DETECTION_API_URL, headers=headers, data=data)

    if response.status_code == 200:
        try:
            return response.json()[0]['label']
        except (KeyError, IndexError, TypeError):
            print("Error: Unexpected API response format.")
            return None
    else:
        print(f"API Error {response.status_code}: {response.text}")
        return None
